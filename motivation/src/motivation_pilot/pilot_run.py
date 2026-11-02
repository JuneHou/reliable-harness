"""Run the motivation pilot on the cases that are ready.

Repair selection uses the public check only. Held-out questions are scored
after the patch is locked. The published fixed programs are a separate
privileged probe and do not choose the baseline patch.
"""

from __future__ import annotations

import csv
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

ARCHIVE = Path("/data/wang/junh/githubs/SelfHeal/AgentDefect.zip")
ROOT = Path(__file__).resolve().parents[2]
REPAIRS = ROOT / "artifacts" / "repairs"
OUT = ROOT / "artifacts" / "pilot_results.json"
PRICE_IN = 0.10 / 1_000_000
PRICE_OUT = 0.50 / 1_000_000

REVISIONS = {
    "77099194": {
        "question": "Return all the action movies names",
        "contract": (
            "Use movies.csv. Return every title whose genres include Action. "
            "Do not add a title that is not tagged Action."
        ),
        "data_file": "movies.csv",
    },
    "78383658": {
        "question": "Find movies for family, combining their Name and Description.",
        "contract": (
            "Use control.csv. Name means the title column and description means the overview column. "
            "Return each film tagged Family. Do not add a film that is not tagged Family."
        ),
        "data_file": "control.csv",
    },
}


def _money(prompt: int, completion: int) -> float:
    return prompt * PRICE_IN + completion * PRICE_OUT


def _study_prelude() -> str:
    return r'''
import json, sys
import langchain.chat_models as chat_models
import langchain_openai
import langchain_openai.chat_models.base as base
class StudyChat(base.ChatOpenAI):
    def __init__(self, *args, **kwargs):
        kwargs.pop("model", None)
        kwargs.pop("model_name", None)
        kwargs["model"] = "gpt-6-luna"
        kwargs["temperature"] = 0
        kwargs["reasoning_effort"] = "none"
        super().__init__(*args, **kwargs)
    def _get_request_payload(self, input_, *, stop=None, **kwargs):
        payload = super()._get_request_payload(input_, stop=None, **kwargs)
        payload.pop("stop", None)
        return payload
base.ChatOpenAI = StudyChat
chat_models.ChatOpenAI = StudyChat
langchain_openai.ChatOpenAI = StudyChat
try:
    import langchain_openai.chat_models as exported
    exported.ChatOpenAI = StudyChat
except Exception:
    pass
try:
    import langchain.chat_models.openai as old
    old.ChatOpenAI = StudyChat
except Exception:
    pass
'''


def _extract(case_id: str, dest: Path) -> None:
    with zipfile.ZipFile(ARCHIVE) as archive:
        for name in archive.namelist():
            if name.startswith(f"AgentDefect/{case_id}/") and not name.endswith("/"):
                rel = name.split("/", 2)[-1]
                path = dest / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(archive.read(name))


def _flatten(result) -> str:
    if isinstance(result, list):
        parts = []
        for item in result:
            parts.append(getattr(item, "page_content", str(item)))
        return "\n".join(parts)
    if isinstance(result, dict):
        return str(result.get("answer") or result.get("output") or result)
    return str(result)


def _tail(value, limit: int = 4000) -> str:
    if isinstance(value, bytes):
        value = value.decode("utf-8", "replace")
    return (value or "")[-limit:]


def _run_instrumented(
    case_id: str,
    module: str,
    question: str,
    source_text: str | None,
    timeout: int,
    trace_path: Path | None,
    turns: list[str] | None,
    probe: bool,
    boundaries: list[str] | None,
) -> dict:
    """One attempt, no retry. The child reports its own phase on failure."""
    from motivation_pilot import instrument

    work = Path(tempfile.mkdtemp(prefix=f"ext-{case_id}-"))
    started = time.time()
    try:
        _extract(case_id, work)
        initial_state = instrument.tree_sha256(work)
        if source_text is not None:
            (work / "run_buggy.py").write_text(source_text, encoding="utf-8")
        prelude = _study_prelude() + instrument.NO_RETRY_PRELUDE
        if probe and trace_path is not None:
            prelude += instrument.trace_prelude(trace_path, boundaries or [])
        else:
            prelude += instrument.NO_PROBE_PRELUDE
        argv = [sys.executable, "-c", instrument.child_script(prelude), module, json.dumps(turns or [question])]
        try:
            proc = subprocess.run(argv, cwd=work, env=os.environ.copy(), capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            return {
                "timeout": True,
                "returncode": None,
                "result": None,
                "initial_state": initial_state,
                "stdout": _tail(exc.stdout),
                "stderr": _tail(exc.stderr),
                "elapsed": round(time.time() - started, 2),
            }
        return {
            "timeout": False,
            "returncode": proc.returncode,
            "result": instrument.last_json(proc.stdout),
            "initial_state": initial_state,
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-4000:],
            "elapsed": round(time.time() - started, 2),
        }
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _run_module(
    case_id: str,
    module: str,
    question: str,
    source_text: str | None,
    timeout: int,
    trace_path: Path | None = None,
    turns: list[str] | None = None,
    probe: bool = True,
    boundaries: list[str] | None = None,
) -> dict:
    if trace_path is not None or turns is not None or not probe or boundaries is not None:
        return _run_instrumented(case_id, module, question, source_text, timeout, trace_path, turns, probe, boundaries)
    work = Path(tempfile.mkdtemp(prefix=f"pilot-{case_id}-"))
    try:
        _extract(case_id, work)
        if source_text is not None:
            (work / "run_buggy.py").write_text(source_text, encoding="utf-8")
        child = _study_prelude() + '''
import run_buggy
module_name = sys.argv[1]
question = sys.argv[2]
if module_name == "run_fixed":
    import run_fixed
    module = run_fixed
else:
    module = run_buggy
from langchain_community.callbacks import get_openai_callback
with get_openai_callback() as cb:
    result = module.run_agent(question)
if isinstance(result, list):
    parts = [getattr(item, "page_content", str(item)) for item in result]
    text = "\\n".join(parts)
    count = len(result)
elif isinstance(result, dict):
    text = str(result.get("answer") or result.get("output") or result)
    count = None
else:
    text = str(result)
    count = None
print(json.dumps({
    "text": text,
    "count": count,
    "prompt": int(cb.prompt_tokens or 0),
    "completion": int(cb.completion_tokens or 0),
}))
'''
        last_error = ""
        for attempt in range(2):
            proc = subprocess.run(
                [sys.executable, "-c", child, module, question],
                cwd=work,
                env=os.environ.copy(),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if proc.returncode == 0:
                payload = json.loads(proc.stdout.strip().splitlines()[-1])
                payload["attempts"] = attempt + 1
                return payload
            last_error = "\n".join(
                line for line in proc.stderr.splitlines()
                if "DeprecationWarning" not in line and "langchain cli" not in line
            )[-800:]
            transient = any(token in last_error for token in ("APIConnectionError", "RateLimit", "InternalServerError", "Timeout"))
            if not transient:
                break
        return {"error": last_error or "execution failed", "prompt": 0, "completion": 0}
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "prompt": 0, "completion": 0}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _titles(case_id: str, filename: str) -> tuple[list[str], list[dict]]:
    with zipfile.ZipFile(ARCHIVE) as archive:
        text = archive.read(f"AgentDefect/{case_id}/{filename}").decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text))), text


def _rows(case_id: str, filename: str) -> list[dict]:
    rows, _ = _titles(case_id, filename)
    return rows


def _score_titles(answer: str, expected: list[str], catalog: list[str]) -> dict:
    low = answer.lower()
    missing = [title for title in expected if title.lower() not in low]
    added = [title for title in catalog if title.lower() in low and title not in expected]
    return {"missing": missing, "added": added, "passed": not missing and not added}


def _genre_titles(rows: list[dict], token: str) -> list[str]:
    return sorted(row["title"] for row in rows if token in row["genres"].split())


def _score_buildings(answer: str, required: list[str], forbidden: list[str] | None = None) -> dict:
    low = answer.lower()
    missing = [phrase for phrase in required if phrase.lower() not in low]
    extra = [phrase for phrase in (forbidden or []) if phrase.lower() in low]
    return {"missing": missing, "forbidden_present": extra, "passed": not missing and not extra}


def _repair_once(source: str, case: dict, failure: str, data_text: str) -> tuple[str, dict]:
    from openai import OpenAI

    prompt = (
        "Diagnose the supplied failure and implement a persistent fix that restores the documented task "
        "while preserving other supported behavior. You may change more than one part of the program when needed. "
        "Return only the complete replacement for run_buggy.py. Do not add markdown.\n\n"
        f"Public task: {case['question']}\n"
        f"Correctness contract: {case['contract']}\n"
        f"Failed public run output:\n{failure[:2000]}\n\n"
        f"Program input file {case['data_file']}:\n{data_text}\n\n"
        "Current run_buggy.py:\n"
        f"{source}"
    )
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-6-luna",
        temperature=0,
        reasoning_effort="none",
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.choices[0].message.content or ""
    usage = response.usage
    meta = {
        "prompt_tokens": int(getattr(usage, "prompt_tokens", 0) or 0),
        "completion_tokens": int(getattr(usage, "completion_tokens", 0) or 0),
    }
    fenced = re.search(r"```(?:python)?\n(.*?)```", text, re.S)
    code = fenced.group(1) if fenced else text
    return code.strip() + "\n", meta


def _public_movie_score(case_id: str, answer: str) -> dict:
    if case_id == "77099194":
        rows = _rows(case_id, "movies.csv")
        expected = _genre_titles(rows, "Action")
        catalog = sorted({row["title"] for row in rows})
        return _score_titles(answer, expected, catalog)
    rows = _rows(case_id, "control.csv")
    expected = _genre_titles(rows, "Family")
    catalog = sorted({row["title"] for row in rows})
    scored = _score_titles(answer, expected, catalog)
    snippets = []
    for row in rows:
        if row["title"] in expected:
            snippet = row["overview"][:40]
            snippets.append({"title": row["title"], "overview_fragment_present": snippet.lower() in answer.lower()})
    scored["overview_fragments"] = snippets
    return scored


def revise_movies() -> dict:
    """Two revisions are allowed. Stop at the first public success.

    Held-out results are not read here. If every public check fails, the last
    revision is locked because it saw the public failure. That choice is not
    based on held-out answers.
    """
    revised = {}
    for case_id, case in REVISIONS.items():
        source = (REPAIRS / case_id / "run_buggy.py").read_text(encoding="utf-8")
        (REPAIRS / case_id / "attempt_1.py").write_text(source, encoding="utf-8")
        selected = source
        attempts = []
        passed = False
        selected_attempt = 1
        for attempt in (1, 2, 3):
            if attempt > 1:
                _, data_text = _titles(case_id, case["data_file"])
                code, usage = _repair_once(selected, case, failure, data_text)
                selected = code
                selected_attempt = attempt
                (REPAIRS / case_id / f"attempt_{attempt}.py").write_text(code, encoding="utf-8")
                attempts.append({"attempt": attempt, "repair_usage": usage})
            run = _run_module(case_id, "run_buggy", case["question"], selected, 180)
            if run.get("error"):
                answer = ""
                score = {"passed": False, "error": run["error"]}
            else:
                answer = run["text"]
                score = _public_movie_score(case_id, answer)
                score["usage"] = {"prompt": run["prompt"], "completion": run["completion"]}
            attempts.append({"attempt": attempt, "check": True, "answer": answer[:1500], "score": score})
            if score.get("passed"):
                passed = True
                selected_attempt = attempt
                break
            failure = answer if answer else score.get("error", "The public run produced no usable answer.")
        (REPAIRS / case_id / "run_buggy.py").write_text(selected, encoding="utf-8")
        revised[case_id] = {
            "selected_attempt": selected_attempt,
            "public_passed": passed,
            "attempts": attempts,
            "selection_rule": "first public success; otherwise the last revision; held-out results were not used",
        }
    return revised


def _repeat(case_id: str, module: str, question: str, source_text: str | None, repetitions: int, timeout: int) -> list[dict]:
    runs = []
    for number in range(1, repetitions + 1):
        result = _run_module(case_id, module, question, source_text, timeout)
        result["repetition"] = number
        runs.append(result)
    return runs


def _arm_summary(runs: list[dict], score_of) -> dict:
    scored = []
    prompt = completion = 0
    for run in runs:
        prompt += int(run.get("prompt") or 0)
        completion += int(run.get("completion") or 0)
        if run.get("error"):
            scored.append({"repetition": run["repetition"], "passed": False, "error": run["error"]})
        else:
            item = score_of(run["text"])
            item["repetition"] = run["repetition"]
            item["answer"] = run["text"][:500]
            scored.append(item)
    return {
        "repetitions": scored,
        "passed_count": sum(1 for item in scored if item.get("passed")),
        "usage": {"prompt": prompt, "completion": completion, "dollars_chat": round(_money(prompt, completion), 4)},
    }


def evaluate() -> dict:
    report = {}
    building_source = (REPAIRS / "77178370" / "run_buggy.py").read_text(encoding="utf-8")
    building_questions = [
        ("public", "What are buildings made of?", ["brick", "wood", "stone"], ["metal", "plastic"]),
        ("related", "What are cars made out of?", ["metal", "plastic"], []),
        ("related", "Which building materials do the notes name?", ["brick", "wood", "stone"], []),
    ]
    building = {"arms": {}}
    for arm, source in (("original", None), ("baseline", building_source)):
        building["arms"][arm] = {}
        for role, question, required, forbidden in building_questions:
            runs = _repeat("77178370", "run_buggy", question, source, 3, 180)
            summary = _arm_summary(runs, lambda text, required=required, forbidden=forbidden: _score_buildings(text, required, forbidden))
            building["arms"][arm][question] = {"role": role, **summary}
    report["77178370"] = building

    movie_plan = {
        "77099194": ("movies.csv", [
            ("public", "Return all the action movies names", "Action"),
            ("related", "Return all the adventure movie names", "Adventure"),
            ("related", "Return all the animation movie names", "Animation"),
        ]),
        "78383658": ("control.csv", [
            ("public", "Find movies for family, combining their Name and Description.", "Family"),
            ("related", "Find movies whose genres include Action. Return each title with its description.", "Action"),
            ("related", "Find movies whose genres include Adventure. Return each title with its description.", "Adventure"),
        ]),
    }
    for case_id, (filename, questions) in movie_plan.items():
        rows = _rows(case_id, filename)
        catalog = sorted({row["title"] for row in rows})
        source = (REPAIRS / case_id / "run_buggy.py").read_text(encoding="utf-8")
        case_report = {"arms": {}}
        for arm, text in (("original", None), ("baseline", source)):
            case_report["arms"][arm] = {}
            for role, question, token in questions:
                expected = _genre_titles(rows, token)
                runs = _repeat(case_id, "run_buggy", question, text, 3, 180)
                summary = _arm_summary(runs, lambda answer, expected=expected, catalog=catalog: _score_titles(answer, expected, catalog))
                case_report["arms"][arm][question] = {"role": role, "expected_count": len(expected), **summary}
        report[case_id] = case_report
    return report


AUDIT_OLD = '''    query = "what are cars made of?"
    result = qa({"question": query})
    result= retriever.get_relevant_documents(query)
    
    return result'''
AUDIT_NEW = '''    result = qa({"question": user_input})
    return result["answer"]'''


def _audit_building_source(source: str) -> str | None:
    """The audit variant: ask the user's question and return the chain answer."""
    if AUDIT_OLD not in source:
        return None
    return source.replace(AUDIT_OLD, AUDIT_NEW, 1)


def audit_buildings() -> dict:
    """Ask whether the baseline's extra retrieval and prompt changes are needed.

    This probe is not the baseline. It keeps the original retriever and prompt,
    and changes only the ignored question and the returned value.
    """
    with zipfile.ZipFile(ARCHIVE) as archive:
        source = archive.read("AgentDefect/77178370/run_buggy.py").decode("utf-8")
    probe = _audit_building_source(source)
    if probe is None:
        return {"status": "not_constructed", "reason": "The original source no longer contains the expected lines."}
    questions = [
        ("What are buildings made of?", ["brick", "wood", "stone"], ["metal", "plastic"]),
        ("What are cars made out of?", ["metal", "plastic"], []),
        ("Which building materials do the notes name?", ["brick", "wood", "stone"], []),
    ]
    results = {}
    for question, required, forbidden in questions:
        run = _run_module("77178370", "run_buggy", question, probe, 180)
        if run.get("error"):
            results[question] = {"passed": False, "error": run["error"]}
        else:
            results[question] = _score_buildings(run["text"], required, forbidden)
            results[question]["answer"] = run["text"][:400]
            results[question]["usage"] = {"prompt": run["prompt"], "completion": run["completion"]}
    return {"label": "audit_use_the_asked_question", "privileged": False, "questions": results}


def privileged_probe() -> dict:
    """Run the published fixed programs once. These results are not baseline scores."""
    probes = {
        "77178370": "What are buildings made of?",
        "77099194": "Return all the action movies names",
        "78383658": "Find movies for family, combining their Name and Description.",
    }
    out = {}
    for case_id, question in probes.items():
        run = _run_module(case_id, "run_fixed", question, None, 180)
        if run.get("error"):
            out[case_id] = {"passed": False, "error": run["error"], "label": "published_fix", "privileged": True}
            continue
        if case_id == "77178370":
            score = _score_buildings(run["text"], ["brick", "wood", "stone"], ["metal", "plastic"])
        elif case_id == "77099194":
            score = _public_movie_score(case_id, run["text"])
        else:
            score = _public_movie_score(case_id, run["text"])
        score["answer"] = run["text"][:400]
        score["usage"] = {"prompt": run["prompt"], "completion": run["completion"]}
        score["label"] = "published_fix"
        score["privileged"] = True
        out[case_id] = score
    return out


def local_checks() -> dict:
    """Score the spreadsheet loader and the PDF search without starting a shell agent."""
    checks = {}
    work = Path(tempfile.mkdtemp(prefix="pilot-local-"))
    try:
        _extract("79343179", work)
        original = (work / "run_buggy.py").read_text(encoding="utf-8")
        patched = (REPAIRS / "79343179" / "run_buggy.py").read_text(encoding="utf-8")
        for name, source in (("original", original), ("baseline", patched)):
            target = work / "loaded.py"
            target.write_text(source, encoding="utf-8")
            child = '''
import json, importlib.util
spec = importlib.util.spec_from_file_location("loaded", "loaded.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
tool = module.load_excel_response
fn = tool.func if hasattr(tool, "func") else tool
frame = fn("excel_file.xlsx")
print(json.dumps({
    "columns": [str(column) for column in frame.columns],
    "rows": int(len(frame)),
    "sentiment": ["" if value != value else str(value) for value in frame["Sentiment"]] if "Sentiment" in frame.columns else [],
    "location": ["" if value != value else str(value) for value in frame["Location"]] if "Location" in frame.columns else [],
}))
'''
            proc = subprocess.run([sys.executable, "-c", child], cwd=work, capture_output=True, text=True, timeout=60)
            if proc.returncode != 0:
                checks.setdefault("79343179", {})[name] = {"passed": False, "error": proc.stderr[-400:]}
                continue
            payload = json.loads(proc.stdout.strip().splitlines()[-1])
            expected_columns = ["UserName", "ScreenName", "Location", "TweetAt", "OriginalTweet", "Sentiment"]
            payload["passed"] = (
                payload["columns"] == expected_columns
                and payload["rows"] == 4
                and payload["sentiment"] == ["Neutral", "Positive", "Positive", "Positive"]
                and payload["location"] == ["London", "UK", "Vagabonds", ""]
            )
            checks.setdefault("79343179", {})[name] = payload
    finally:
        shutil.rmtree(work, ignore_errors=True)

    pdf_questions = "https://arxiv.org/pdf/2303.08774.pdf"
    original_runs = _repeat("78366661", "run_buggy", pdf_questions, None, 3, 240)
    patch = (REPAIRS / "78366661" / "run_buggy.py").read_text(encoding="utf-8")
    patch_runs = _repeat("78366661", "run_buggy", pdf_questions, patch, 3, 240)

    def pdf_score(runs: list[dict]) -> dict:
        scored = []
        for run in runs:
            if run.get("error"):
                scored.append({"repetition": run["repetition"], "passed": False, "error": run["error"]})
            else:
                count = run.get("count")
                if count is None:
                    count = 0 if not run.get("text") else 1
                scored.append({"repetition": run["repetition"], "count": count, "passed": count > 0})
        return {"repetitions": scored, "passed_count": sum(1 for item in scored if item.get("passed"))}

    checks["78366661"] = {"original": pdf_score(original_runs), "baseline": pdf_score(patch_runs)}
    return checks


def not_repaired() -> list[dict]:
    return [
        {
            "case_id": "76897509",
            "reason": "Under gpt-6-luna the program answered from the papers. The question was not changed.",
        },
        {
            "case_id": "78838421",
            "reason": "Under the OpenAI adaptation the program returned a nonempty answer and the crash did not return. The question was not changed.",
        },
        {
            "case_id": "79149108",
            "reason": "Horse, elephant, and car were answered correctly. The missing assistant history did not change those answers, so no repair was started from a failure that was not observed.",
        },
    ]


def main() -> None:
    results = {
        "model": "gpt-6-luna",
        "temperature": 0,
        "reasoning_effort": "none",
        "selection_rule": "first public success, at most two revisions, held-out not used",
        "not_repaired": not_repaired(),
        "revisions": revise_movies(),
    }
    OUT.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print("revisions locked", flush=True)
    results["evaluation"] = evaluate()
    OUT.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print("evaluation done", flush=True)
    results["local_checks"] = local_checks()
    results["audit"] = {"77178370": audit_buildings()}
    results["privileged"] = privileged_probe()
    OUT.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
