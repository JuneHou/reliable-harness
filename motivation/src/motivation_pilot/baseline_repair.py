"""Baseline repair for cases that still fail under gpt-6-luna.

The repair agent sees the buggy program, the public task, and the failed run.
It does not see the published fix or the held-out questions.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ARCHIVE = Path("/data/wang/junh/githubs/SelfHeal/AgentDefect.zip")
OUT = Path(__file__).resolve().parents[2] / "artifacts" / "baseline_repairs.json"

CASES = {
    "77178370": {
        "question": "What are buildings made of?",
        "contract": (
            "Answer from the building notes stored in the program. "
            "Include each building material those notes name. Do not answer from the car notes."
        ),
        "failure": "The original run returned notes about cars, atoms, and 'building materials', and missed brick, wood, and stone.",
    },
    "77099194": {
        "question": "Return all the action movies names",
        "contract": (
            "Use movies.csv. Return every title whose genres include Action. "
            "Do not add a title that is not tagged Action."
        ),
        "failure": "Under gpt-6-luna the original program named only Avengers: Age of Ultron.",
    },
    "78383658": {
        "question": "Find movies for family, combining their Name and Description.",
        "contract": (
            "Use control.csv. Name means the title column and description means the overview column. "
            "Return each film tagged Family. Do not add a film that is not tagged Family."
        ),
        "failure": "Under gpt-6-luna the original program named Tangled, Avatar, and John Carter, and missed Harry Potter.",
    },
    "78366661": {
        "question": "Search the GPT-4 paper for how much compute training used, and return the matching passages.",
        "contract": "The search result must not be an empty list. The current search object returns [] for every query.",
        "failure": "DummyVectorSearch.similarity_search returns an empty list.",
    },
    "79343179": {
        "question": "Load excel_file.xlsx and return the table.",
        "contract": (
            "The sheet has four rows and the columns UserName, ScreenName, Location, TweetAt, OriginalTweet, and Sentiment. "
            "The current loader uses skiprows=2 and one column named responses, so the first two rows and the real column names are lost."
        ),
        "failure": "The loader result is two cells, both the word Positive.",
    },
}


def _extract(case_id: str, dest: Path) -> None:
    with zipfile.ZipFile(ARCHIVE) as archive:
        for name in archive.namelist():
            if name.startswith(f"AgentDefect/{case_id}/") and not name.endswith("/"):
                rel = name.split("/", 2)[-1]
                if Path(rel).name == "run_fixed.py":
                    continue
                path = dest / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(archive.read(name))


def _repair_call(source: str, case: dict) -> tuple[str, dict]:
    from openai import OpenAI

    prompt = (
        "Diagnose the supplied failure and implement a persistent fix that restores the documented task "
        "while preserving other supported behavior. You may change more than one part of the program when needed. "
        "Return only the complete replacement for run_buggy.py. Do not add markdown.\n\n"
        f"Public task: {case['question']}\n"
        f"Correctness contract: {case['contract']}\n"
        f"Failed run: {case['failure']}\n\n"
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


def _run_loader(work: Path) -> dict:
    code = """
import json
import run_buggy
tool = run_buggy.load_excel_response
fn = tool.func if hasattr(tool, "func") else tool
frame = fn("excel_file.xlsx")
print(json.dumps({"columns": [str(name) for name in frame.columns], "rows": int(len(frame))}))
"""
    proc = subprocess.run([sys.executable, "-c", code], cwd=work, capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        return {"passed": False, "detail": proc.stderr[-400:]}
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    expected = ["UserName", "ScreenName", "Location", "TweetAt", "OriginalTweet", "Sentiment"]
    passed = payload["columns"] == expected and payload["rows"] == 4
    return {"passed": passed, "detail": payload}


def _run_pdf_search(work: Path) -> dict:
    code = """
import json
import run_buggy
rows = run_buggy.run_agent("https://arxiv.org/pdf/2303.08774.pdf")
print(json.dumps({"count": len(rows)}))
"""
    proc = subprocess.run([sys.executable, "-c", code], cwd=work, capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        return {"passed": False, "detail": proc.stderr[-400:]}
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    return {"passed": payload["count"] > 0, "detail": payload}


def _public_check(case_id: str, work: Path, code: str) -> dict:
    path = work / "run_buggy.py"
    path.write_text(code, encoding="utf-8")
    if case_id == "78366661":
        return _run_pdf_search(work)
    if case_id == "79343179":
        return _run_loader(work)
    runner = r'''
import json, sys
import langchain.chat_models as chat_models
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
try:
    import langchain.chat_models.openai as old
    old.ChatOpenAI = StudyChat
except Exception:
    pass
import run_buggy
from langchain_community.callbacks import get_openai_callback
question = sys.argv[1]
with get_openai_callback() as cb:
    result = run_buggy.run_agent(question)
if isinstance(result, dict):
    text = result.get("answer") or result.get("output") or str(result)
else:
    text = str(result)
print(json.dumps({"text": text[:1500], "prompt": int(cb.prompt_tokens or 0), "completion": int(cb.completion_tokens or 0)}))
'''
    question = CASES[case_id]["question"]
    proc = subprocess.run(
        [sys.executable, "-c", runner, question],
        cwd=work,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if proc.returncode != 0:
        err = "\n".join(line for line in proc.stderr.splitlines() if "Deprecation" not in line)
        return {"passed": False, "detail": err[-500:]}
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    text = payload["text"]
    if case_id == "77178370":
        low = text.lower()
        missing = [word for word in ("brick", "wood", "stone") if word not in low]
        cars = [word for word in ("metal", "plastic") if word in low]
        passed = not missing and not cars
    elif case_id == "77099194":
        expected = [
            "Avatar", "Avengers: Age of Ultron", "Batman v Superman: Dawn of Justice", "John Carter",
            "Pirates of the Caribbean: At World's End", "Quantum of Solace", "Spectre", "Spider-Man 3",
            "Superman Returns", "The Dark Knight Rises",
        ]
        low = text.lower()
        passed = all(title.lower() in low for title in expected)
    else:
        low = text.lower()
        passed = "tangled" in low and "harry potter" in low and "avatar" not in low and "john carter" not in low
    return {"passed": passed, "answer": text, "usage": {"prompt": payload["prompt"], "completion": payload["completion"]}}


def repair_case(case_id: str) -> dict:
    work = Path(tempfile.mkdtemp(prefix=f"repair-{case_id}-"))
    try:
        _extract(case_id, work)
        source = (work / "run_buggy.py").read_text(encoding="utf-8")
        code, usage = _repair_call(source, CASES[case_id])
        check = _public_check(case_id, work, code)
        saved = Path(__file__).resolve().parents[2] / "artifacts" / "repairs" / case_id
        saved.mkdir(parents=True, exist_ok=True)
        (saved / "run_buggy.py").write_text(code, encoding="utf-8")
        return {
            "case_id": case_id,
            "model": "gpt-6-luna",
            "repair_usage": usage,
            "public_check": check,
            "patch_path": str(saved / "run_buggy.py"),
        }
    except Exception as exc:
        return {"case_id": case_id, "status": "error", "detail": f"{type(exc).__name__}: {exc}"[:500]}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main() -> None:
    results = [repair_case(case_id) for case_id in CASES]
    OUT.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
