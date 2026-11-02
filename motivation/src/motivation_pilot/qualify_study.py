"""Run each runnable original program once under gpt-6-luna.

The animal-game and love-quotes programs call Ollama. That local server is not
installed. On the user's instruction, those calls are sent to OpenAI instead.
The published source files are not edited. The same replacement is applied
before either version of a program is imported.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ARCHIVE = Path("/data/wang/junh/githubs/SelfHeal/AgentDefect.zip")
OUT = Path(__file__).resolve().parents[2] / "artifacts" / "qualification_gpt6.json"

PRICE_IN = 0.10 / 1_000_000
PRICE_OUT = 0.50 / 1_000_000
PRICE_EMBED = 0.10 / 1_000_000

CASES = {
    "77178370": {
        "question": "What are buildings made of?",
        "kind": "buildings",
    },
    "77099194": {
        "question": "Return all the action movies names",
        "kind": "titles",
        "csv": "movies.csv",
        "token": "Action",
    },
    "78383658": {
        "question": "Find movies for family, combining their Name and Description.",
        "kind": "titles",
        "csv": "control.csv",
        "token": "Family",
    },
    "76897509": {
        "question": "What is Theia",
        "kind": "theia",
    },
}


def _install_model() -> None:
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
    try:
        import langchain_community.chat_models.openai as community
        community.ChatOpenAI = StudyChat
    except Exception:
        pass


def _titles(csv_path: Path, token: str) -> tuple[list[str], list[str]]:
    import csv
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    expected = sorted(row["title"] for row in rows if token in row["genres"].split())
    catalog = sorted({row["title"] for row in rows})
    return expected, catalog


def _score_titles(answer: str, expected: list[str], catalog: list[str]) -> dict:
    low = answer.lower()
    missing = [title for title in expected if title.lower() not in low]
    added = [title for title in catalog if title.lower() in low and title not in expected]
    return {"missing": missing, "added": added, "passed": not missing and not added}


def _score_buildings(answer: str) -> dict:
    low = answer.lower()
    required = ["brick", "wood", "stone"]
    missing = [word for word in required if word not in low]
    car = [word for word in ("metal", "plastic") if word in low]
    return {"missing_materials": missing, "car_materials_present": car, "passed": not missing and not car}


def _money(prompt: int, completion: int, embed: int = 0) -> float:
    return prompt * PRICE_IN + completion * PRICE_OUT + embed * PRICE_EMBED


def run_case(case_id: str, spec: dict) -> dict:
    work = Path(tempfile.mkdtemp(prefix=f"qual-{case_id}-"))
    try:
        with zipfile.ZipFile(ARCHIVE) as archive:
            for name in archive.namelist():
                if name.startswith(f"AgentDefect/{case_id}/") and not name.endswith("/"):
                    dest = work / name.split("/", 2)[-1]
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(archive.read(name))
        env = os.environ.copy()
        env["PYTHONPATH"] = str(work)
        code = r'''
import json, sys
sys.path.insert(0, sys.argv[1])
question = sys.argv[2]
kind = sys.argv[3]
# patch before the case imports its model class
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
try:
    import langchain_community.chat_models.openai as community
    community.ChatOpenAI = StudyChat
except Exception:
    pass
if kind == "theia":
    import langchain.llms.openai as llms
    llms.OpenAI = StudyChat
usage = {"prompt": 0, "completion": 0}
try:
    from langchain_community.callbacks import get_openai_callback
except Exception:
    get_openai_callback = None
import run_buggy
def call():
    if kind == "theia":
        return run_buggy.run_agent(question, ["paper1.pdf", "paper2.pdf"])
    return run_buggy.run_agent(question)
if get_openai_callback is not None:
    with get_openai_callback() as cb:
        result = call()
        usage["prompt"] = int(getattr(cb, "prompt_tokens", 0) or 0)
        usage["completion"] = int(getattr(cb, "completion_tokens", 0) or 0)
else:
    result = call()
if isinstance(result, dict):
    text = result.get("answer") or result.get("output") or str(result)
else:
    text = str(result)
print(json.dumps({"text": text[:2000], "usage": usage}))
'''
        proc = subprocess.run(
            [sys.executable, "-c", code, str(work), spec["question"], spec["kind"]],
            cwd=work,
            env=env,
            capture_output=True,
            text=True,
            timeout=240,
        )
        if proc.returncode != 0:
            err = "\n".join(
                line for line in proc.stderr.splitlines()
                if "DeprecationWarning" not in line and "langchain cli" not in line
            )
            return {"case_id": case_id, "status": "error", "detail": err[-800:], "question": spec["question"]}
        payload = json.loads(proc.stdout.strip().splitlines()[-1])
        text = payload["text"]
        record = {
            "case_id": case_id,
            "status": "ran",
            "question": spec["question"],
            "model": "gpt-6-luna",
            "temperature": 0,
            "reasoning_effort": "none",
            "answer": text,
            "usage": payload["usage"],
        }
        if spec["kind"] == "titles":
            expected, catalog = _titles(work / spec["csv"], spec["token"])
            record["score"] = _score_titles(text, expected, catalog)
            record["expected_titles"] = expected
        elif spec["kind"] == "buildings":
            record["score"] = _score_buildings(text)
        else:
            record["score"] = {"passed": None, "note": "published check is a don't-know phrase; recorded, not forced"}
        tokens = record["usage"]
        record["dollars_chat"] = round(_money(tokens["prompt"], tokens["completion"]), 4)
        return record
    except subprocess.TimeoutExpired:
        return {"case_id": case_id, "status": "timeout", "question": spec["question"]}
    finally:
        shutil.rmtree(work, ignore_errors=True)


ADAPTATION = {
    "provenance": "User instruction: do not stop; use OpenAI.",
    "published_files": "unchanged",
    "applied_before_import": True,
    "chat_model": "gpt-6-luna",
    "temperature": 0,
    "reasoning_effort": "none",
    "embeddings": "OpenAIEmbeddings default",
    "pdf_read_strategy": "fast",
    "pdf_read_reason": (
        "The published loader's default strategy imports unstructured_inference. "
        "That package is not installed. The fast strategy reads the same text PDF."
    ),
}


def _adapted_prelude() -> str:
    return r'''
import types, sys
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_openai.embeddings.base import OpenAIEmbeddings

class StudyChat(ChatOpenAI):
    def __init__(self, *args, **kwargs):
        kwargs.pop("model", None)
        kwargs.pop("model_name", None)
        kwargs.pop("stream", None)
        kwargs["model"] = "gpt-6-luna"
        kwargs["temperature"] = 0
        kwargs["reasoning_effort"] = "none"
        super().__init__(*args, **kwargs)
    def _get_request_payload(self, input_, *, stop=None, **kwargs):
        payload = super()._get_request_payload(input_, stop=None, **kwargs)
        payload.pop("stop", None)
        return payload

class StudyEmbeddings(OpenAIEmbeddings):
    def __init__(self, *args, **kwargs):
        kwargs.pop("model", None)
        kwargs.pop("show_progress", None)
        super().__init__(*args, **kwargs)

ollama_mod = types.ModuleType("ollama")
def _ollama_chat(*args, **kwargs):
    raise RuntimeError("The published ollama.chat call was reached. This run uses OpenAI.")
ollama_mod.chat = _ollama_chat
sys.modules["ollama"] = ollama_mod
ollama_chat = types.ModuleType("langchain_ollama")
ollama_chat.ChatOllama = StudyChat
sys.modules["langchain_ollama"] = ollama_chat

import langchain_community.chat_models as community_chat
import langchain_community.embeddings as community_embeddings
import langchain_community.document_loaders as community_loaders
from langchain_community.document_loaders.pdf import UnstructuredPDFLoader
community_chat.ChatOllama = StudyChat
community_embeddings.OllamaEmbeddings = StudyEmbeddings
_orig_init = UnstructuredPDFLoader.__init__
def _init(self, file_path, mode="single", **kwargs):
    kwargs.setdefault("strategy", "fast")
    _orig_init(self, file_path, mode=mode, **kwargs)
UnstructuredPDFLoader.__init__ = _init
community_loaders.UnstructuredPDFLoader = UnstructuredPDFLoader
'''


def _run_adapted(case_id: str, child: str, timeout: int) -> dict:
    work = Path(tempfile.mkdtemp(prefix=f"adapt-{case_id}-"))
    try:
        with zipfile.ZipFile(ARCHIVE) as archive:
            for name in archive.namelist():
                if name.startswith(f"AgentDefect/{case_id}/") and not name.endswith("/"):
                    dest = work / name.split("/", 2)[-1]
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(archive.read(name))
        proc = subprocess.run(
            [sys.executable, "-c", _adapted_prelude() + child, str(work)],
            cwd=work,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if proc.returncode != 0:
            err = "\n".join(
                line for line in proc.stderr.splitlines()
                if "DeprecationWarning" not in line and "langchain cli" not in line
            )
            return {"case_id": case_id, "status": "error", "detail": err[-800:], "adaptation": ADAPTATION}
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except subprocess.TimeoutExpired:
        return {"case_id": case_id, "status": "timeout", "adaptation": ADAPTATION}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _yes_no(text: str) -> str:
    token = text.strip().lower().split()[:1]
    word = token[0].strip(".,!") if token else ""
    if word in {"yes", "no"}:
        return word
    return "other"


def run_animal() -> dict:
    child = r'''
import json, sys
sys.path.insert(0, sys.argv[1])
import run_buggy
from langchain_community.callbacks import get_openai_callback
turns = [
    "We are gonna play a game in which I'm gonna say some words and you have to tell me if the word represents an animal. Just tell me yes or no.",
    "horse",
    "elephant",
    "car",
    "ok stop the game, let's do something else",
]
run_buggy.messages.clear()
client = run_buggy.app.test_client()
answers = []
with get_openai_callback() as cb:
    for text in turns:
        response = client.post("/ask_gpt", data={"text": text})
        answers.append(response.get_data(as_text=True))
history = []
for item in run_buggy.messages:
    if isinstance(item, tuple) and len(item) == 2:
        history.append({"stored_as": "tuple", "role": str(item[0])})
    elif isinstance(item, dict):
        history.append({"stored_as": "dict", "role": str(item.get("role"))})
    else:
        history.append({"stored_as": type(item).__name__, "role": ""})
print(json.dumps({
    "case_id": "79149108",
    "status": "ran",
    "model": "gpt-6-luna",
    "temperature": 0,
    "reasoning_effort": "none",
    "answers": answers,
    "history": history,
    "usage": {"prompt": int(cb.prompt_tokens or 0), "completion": int(cb.completion_tokens or 0)},
}))
'''
    record = _run_adapted("79149108", child, 180)
    if record.get("status") != "ran":
        return record
    expected = {"horse": "yes", "elephant": "yes", "car": "no"}
    words = ["instruction", "horse", "elephant", "car", "stop"]
    scored = []
    for word, answer in zip(words, record["answers"]):
        item = {"turn": word, "answer": answer, "read_as": _yes_no(answer)}
        if word in expected:
            item["expected"] = expected[word]
            item["matched"] = item["read_as"] == expected[word]
        scored.append(item)
    assistant_stored = any(item["role"] == "assistant" for item in record["history"])
    record["turns"] = scored
    record["assistant_reply_stored"] = assistant_stored
    record["yes_no_matched"] = all(item.get("matched", True) for item in scored)
    record["adaptation"] = ADAPTATION
    tokens = record["usage"]
    record["dollars_chat"] = round(_money(tokens["prompt"], tokens["completion"]), 4)
    record["observation"] = (
        "The assistant reply is still absent from the stored history."
        if not assistant_stored
        else "The stored history includes an assistant reply. The published omission was not observed."
    )
    return record


def run_quotes() -> dict:
    child = r'''
import json, sys
sys.path.insert(0, sys.argv[1])
import run_buggy
from langchain_community.callbacks import get_openai_callback
question = "Give 10 quotes from this articles related to love?"
with get_openai_callback() as cb:
    result = run_buggy.run_agent(question)
text = None if result is None else str(result)
print(json.dumps({
    "case_id": "78838421",
    "status": "ran",
    "model": "gpt-6-luna",
    "temperature": 0,
    "reasoning_effort": "none",
    "question": question,
    "answer": None if text is None else text[:2000],
    "answer_is_none": result is None,
    "usage": {"prompt": int(cb.prompt_tokens or 0), "completion": int(cb.completion_tokens or 0)},
}))
'''
    record = _run_adapted("78838421", child, 600)
    if record.get("status") != "ran":
        return record
    text = record.get("answer") or ""
    record["published_nonempty_string"] = isinstance(record.get("answer"), str) and len(text.strip()) > 1
    record["adaptation"] = ADAPTATION
    tokens = record["usage"]
    record["dollars_chat"] = round(_money(tokens["prompt"], tokens["completion"]), 4)
    if record["answer_is_none"]:
        record["observation"] = "The program returned None. The published nonempty-string check fails."
    elif record["published_nonempty_string"]:
        record["observation"] = "The program returned a nonempty string. The published check would pass. No gold quote list exists, so quote quality was not scored."
    else:
        record["observation"] = "The program returned an empty string."
    return record


def main_adapted() -> None:
    animal = run_animal()
    print(animal.get("case_id"), animal.get("status"), flush=True)
    quotes = run_quotes()
    print(quotes.get("case_id"), quotes.get("status"), flush=True)
    existing = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {"runs": [], "not_run": []}
    done = {animal["case_id"], quotes["case_id"]}
    existing["runs"] = [row for row in existing.get("runs", []) if row.get("case_id") not in done]
    existing["runs"].extend([animal, quotes])
    existing["not_run"] = [row for row in existing.get("not_run", []) if row.get("case_id") not in done]
    existing["openai_adaptation"] = ADAPTATION
    OUT.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    print(OUT)


def main() -> None:
    results = []
    for case_id, spec in CASES.items():
        print(case_id, flush=True)
        results.append(run_case(case_id, spec))
    blocked = [
        {"case_id": "79149108", "status": "environment_blocked", "reason": "Ollama is not installed. No model was substituted."},
        {"case_id": "78838421", "status": "environment_blocked", "reason": "Ollama is not installed. No model was substituted."},
        {"case_id": "79343179", "status": "loader_only", "reason": "The loader defect is already recorded. The full agent was not started because it can run shell commands."},
        {"case_id": "78366661", "status": "local_defect", "reason": "The search returns an empty list without a model call. No second repair was added."},
    ]
    OUT.write_text(json.dumps({"runs": results, "not_run": blocked}, indent=2) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "adapted":
        main_adapted()
    else:
        main()
