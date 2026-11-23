"""Model routing audit (fix plan departure 8, Jun "4 Audits"), AgentDefect.

During a test the relay sends every chat call of the repaired program to the rerun's ARC model,
whatever model the program names. A repair that changes the program's model therefore has that change
replaced. For every tested attempt (kept reruns and replaced first attempts) this audit finds the model
names in the buggy code and in the repair: string constants passed as model, model_name,
deployment_name, model_id or repo_id, and string constants that look like model names (gpt-, o1, o3,
text-embedding, claude, gemini, llama, mistral, mixtral, qwen, deepseek, zephyr, huggingfaceh4). When
the two sets differ, it reads the test's relay log for the chat models the program asked for and the
model that served them. Embedding calls go to OpenAI under the model the program names and are listed
apart. Writes audit_models.csv. Nothing is changed and nothing is run again.

  python audit_models.py
"""
import ast
import csv
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_repairs import INPUTS, MODELS, ROOT, ZIP, final_code  # noqa: E402
import zipfile  # noqa: E402

KEYS = {"model", "model_name", "deployment_name", "model_id", "repo_id", "llm_model", "embedding_model"}
LOOKS = re.compile(r"^(gpt-|o1|o3|o4|text-embedding|claude|gemini|llama|mistral|mixtral|qwen|deepseek|zephyr|huggingfaceh4|meta-llama)", re.I)


def model_names(src):
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg in KEYS and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            out.add(node.value.value)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and LOOKS.match(node.value) \
                and len(node.value) < 80 and " " not in node.value:
            out.add(node.value)
    return out


def buggy(case):
    if case == "hf-26":
        return open(os.path.join(INPUTS, "hf-26_run_buggy.py"), encoding="utf-8").read()
    z = zipfile.ZipFile(ZIP)
    return z.read(f"AgentDefect/{case}/run_buggy.py").decode("utf-8", "replace")


def relay_models(test_dir):
    chat_asked, chat_served, emb = set(), set(), set()
    p = os.path.join(test_dir, "relay_log_test.jsonl")
    if not os.path.exists(p):
        return chat_asked, chat_served, emb
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        path = str(r.get("path", ""))
        if "embeddings" in path:
            emb.add(str(r.get("embed_model") or (r.get("request") or {}).get("model")))
        elif "chat/completions" in path or "completions" in path:
            chat_asked.add(str(r.get("client_model") or (r.get("request") or {}).get("model")))
            chat_served.add(str(r.get("sent_model")))
    return chat_asked, chat_served, emb


def main():
    rows, counts = [], {}
    for m in MODELS:
        folders = sorted(glob.glob(os.path.join(ROOT, m, "[0-9h]*", "rerun_*"))) + \
                  sorted(glob.glob(os.path.join(ROOT, m, "_search_failed", "*", "rerun_*")))
        c = counts.setdefault(m, {"tested attempts": 0, "model names changed": 0, "changed and asked in the test": 0,
                                  "repair's own chat model replaced": 0})
        for d in folders:
            case = os.path.basename(os.path.dirname(d))
            t = os.path.join(d, "test")
            if not os.path.exists(os.path.join(t, "test_record.json")):
                continue
            c["tested attempts"] += 1
            try:
                fixed = final_code(d)
            except RuntimeError:
                continue
            b, f = model_names(buggy(case)), model_names(fixed)
            if b is None or f is None or b == f:
                continue
            c["model names changed"] += 1
            asked, served, emb = relay_models(t)
            added = f - b
            replaced = sorted(x for x in added if x in asked and x not in served)
            c["changed and asked in the test"] += bool(added & asked)
            c["repair's own chat model replaced"] += bool(replaced)
            rows.append({"model": m, "attempt": os.path.relpath(d, ROOT), "buggy_names": "; ".join(sorted(b)),
                         "repair_names": "; ".join(sorted(f)), "added_by_repair": "; ".join(sorted(added)),
                         "removed_by_repair": "; ".join(sorted(b - f)), "chat_asked_in_test": "; ".join(sorted(asked)),
                         "chat_served_by": "; ".join(sorted(served)), "embedding_models": "; ".join(sorted(emb)),
                         "repair_model_replaced": "; ".join(replaced)})
    path = os.path.join(ROOT, "audit_models.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["model"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} attempts with changed model names written to {path}")
    print("| model | tested attempts | model names changed | changed name asked in the test | repair's own chat model replaced |")
    print("|---|---|---|---|---|")
    for m, c in counts.items():
        rep = c["repair's own chat model replaced"]
        print(f"| {m} | {c['tested attempts']} | {c['model names changed']} | {c['changed and asked in the test']} | {rep} |")


if __name__ == "__main__":
    main()
