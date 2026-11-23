"""Run SelfHeal's own steps on AgentIssue-Bench, one ARC model at a time.

The AgentDefect driver (AgentDefect/SelfHeal/code/driver.py) is reused unchanged, with its ROOT and
INPUTS set to this dataset's folders. relay.py and run_agent.py come from the AgentDefect code folder.

  python driver.py rules  --model gpt-oss-120b
      Fix rules (SelfHeal paper 3.1) and the code intents, in AgentIssue-Bench/SelfHeal/<model>/rules/,
      by the AgentDefect driver's rules step.
  python driver.py pick   --model gpt-oss-120b
      For each issue whose report names no repository file, the model picks files with Agentless's
      file prompt (Agentless/agentless/fl/FL.py lines 29 to 48, commit 1d498dec), system message
      "You are a helpful assistant.", temperature 0, one sample, no length limit. Each reply line
      equal to a repository path is a picked file, in reply order. Once per issue and model, in
      <model>/<tag>/pick/.
  python driver.py repair --model gpt-oss-120b --reruns 5 --parallel 5 [--tags TAG ...]
      SelfHeal's fix agent and critic loop (3.2) for every issue and rerun, in
      <model>/<tag>/rerun_<k>/. The named files, or else the picked files, are joined as Agentless
      shows several files (Agentless/agentless/repair/repair.py line 266), "### <path>", the file's
      text, two empty lines, and written as the rerun's run_buggy.py. The issue's reproduction
      script is written as its test.py. run_agent.py runs unchanged. No program is run.
  python driver.py redo   --model gpt-oss-120b
      Reruns with no result file, or with "Search error" in a tool reply, are moved to
      <model>/_stopped/ or <model>/_search_failed/ and run once more. A rerun already redone once
      is not moved again.

Every model call goes through relay.py to the ARC model named by --model, and every request with its
real reply is saved in the step's relay log.
"""
import argparse
import csv
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

AD_CODE = "/data/wang/junh/githubs/stochastic-harness/AgentDefect/SelfHeal/code"
ROOT = "/data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/SelfHeal"
INPUTS = os.path.join(ROOT, "inputs")
ISSUES = os.path.join(INPUTS, "issues")
MODELS = ["gpt-oss-120b", "GLM-5.3", "DeepSeek-V4.1-Flash"]
# The adapted SelfHeal configuration (fix plan, departure 6, Jun "choice 2"), built by build_adapted.py.
# Reruns of the first adaptation, which ran AgentDefect's run_agent.py, are in <model>/_initial_adaptation/.
CONFIGURATION = "adapted"
AGENT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_agent_adapted.py")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ad = load("ad_driver", os.path.join(AD_CODE, "driver.py"))
ad.ROOT, ad.INPUTS = ROOT, INPUTS
move_aside = load("ad_move_aside", os.path.join(AD_CODE, "move_aside.py"))
csv.field_size_limit(10**9)

# With --provider openrouter, every relay of this run sends the model's calls to OpenRouter under the
# name below, with OpenRouter's default routing (Jun "let's try with open router for deep seek",
# "Default routing", "2": the DeepSeek-V4.1-Flash reruns not yet started). Each rerun's run record
# names its provider. Without the option the relays go to ARC as before.
PROVIDER = "arc"
OPENROUTER_KEY_FILE = "/data/wang/junh/.cache/keys/openrouter.sh"
OPENROUTER_MODELS = {"DeepSeek-V4.1-Flash": "deepseek/deepseek-v4.1-flash"}


def use_openrouter(model):
    global PROVIDER
    if model not in OPENROUTER_MODELS:
        raise SystemExit(f"no OpenRouter name for {model}")
    PROVIDER = "openrouter"

    def start_relay(m, log_path):
        port_file = log_path + ".port"
        if os.path.exists(port_file):
            os.remove(port_file)
        proc = subprocess.Popen([ad.PY_NEW, os.path.join(ad.CODE, "relay.py"), "--model", m,
                                 "--log", log_path, "--port-file", port_file,
                                 "--provider", "openrouter", "--provider-model", OPENROUTER_MODELS[m],
                                 "--provider-key-file", OPENROUTER_KEY_FILE])
        for _ in range(100):
            if os.path.exists(port_file) and open(port_file).read().strip():
                return proc, int(open(port_file).read())
            time.sleep(0.1)
        proc.kill()
        raise RuntimeError("relay did not start")

    ad.start_relay = start_relay

# Agentless/agentless/fl/FL.py lines 29 to 48, unchanged.
OBTAIN_RELEVANT_FILES_PROMPT = """
Please look through the following GitHub problem description and Repository structure and provide a list of files that one would need to edit to fix the problem.

### GitHub Problem Description ###
{problem_statement}

###

### Repository Structure ###
{structure}

###

Please only provide the full path and return at most 5 files.
The returned files should be separated by new lines ordered by most to least important and wrapped with ```
For example:
```
file1.py
file2.py
```
"""
SYSTEM_MESSAGE = "You are a helpful assistant."   # Agentless/agentless/util/api_requests.py create_chatgpt_config


def tags_all():
    return sorted(json.load(open(os.path.join(INPUTS, "named_files.json"))))


def reports():
    return {r["id"]: (r["title"], r["body"]) for r in
            csv.DictReader(open(os.path.join(INPUTS, "test_descriptions.csv"), encoding="utf-8"))}


def repo_files(tag):
    return [f for f in open(os.path.join(ISSUES, tag, "files.txt")).read().split("\n") if f]


def pick(model):
    import openai
    named = json.load(open(os.path.join(INPUTS, "named_files.json")))
    rep = reports()
    for tag in sorted(named):
        if named[tag]:
            continue
        d = os.path.join(ROOT, model, tag, "pick")
        if os.path.exists(os.path.join(d, "pick.json")):
            print(tag, "picked before", flush=True)
            continue
        os.makedirs(d, exist_ok=True)
        files = repo_files(tag)
        title, body = rep[tag]
        message = OBTAIN_RELEVANT_FILES_PROMPT.format(problem_statement=f"{title}\n{body}",
                                                      structure="\n".join(files)).strip()
        log = os.path.join(d, "relay_log_pick.jsonl")
        proc, port = ad.start_relay(model, log)
        t0 = time.time()
        try:
            client = openai.OpenAI(api_key=ad.arc_key(), base_url=f"http://127.0.0.1:{port}/v1")
            resp = client.chat.completions.create(
                model=model, temperature=0, n=1,
                messages=[{"role": "system", "content": SYSTEM_MESSAGE}, {"role": "user", "content": message}])
            reply = resp.choices[0].message.content or ""
            error = None
        except Exception as e:
            reply, error = "", f"{type(e).__name__}: {e}"
        finally:
            proc.terminate()
            proc.wait()
        lines = reply.strip().split("\n")          # Agentless _parse_model_return_lines
        fset = set(files)
        picked = []
        for line in lines:                          # Agentless correct_file_paths, a repeated path kept once
            if line in fset and line not in picked:
                picked.append(line)
        rec = {"tag": tag, "model": model, "prompt_chars": len(message), "reply": reply, "picked": picked,
               "error": error, "seconds": round(time.time() - t0, 1), "relay_log": os.path.basename(log)}
        if error is None:
            json.dump(rec, open(os.path.join(d, "pick.json"), "w"), indent=1)
        else:
            ad.save_record(os.path.join(d, "pick_errors.json"), rec)
        print(tag, "picked", picked, error or "", flush=True)


def input_files(model, tag):
    named = json.load(open(os.path.join(INPUTS, "named_files.json")))[tag]
    if named:
        return named, "named"
    p = os.path.join(ROOT, model, tag, "pick", "pick.json")
    if not os.path.exists(p):
        return [], "not picked"
    return json.load(open(p))["picked"], "picked"


def joined_text(tag, files):
    """Agentless/agentless/repair/repair.py line 266: f"### {pred_file}\\n{content}\\n\\n\\n"."""
    parts, not_utf8 = [], []
    for f in files:
        raw = open(os.path.join(ISSUES, tag, "repo", f), "rb").read()
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            content = raw.decode("utf-8", "replace")
            not_utf8.append(f)
        parts.append(f"### {f}\n{content}\n\n\n")
    return "".join(parts), not_utf8


def test_text(tag):
    for ext in ("py", "js"):
        p = os.path.join(ISSUES, tag, f"test.{ext}")
        if os.path.exists(p):
            return open(p, encoding="utf-8").read()
    raise RuntimeError(f"{tag}: no test text")


# Fix plan departure 14 (Jun "Yes, rerun the seven"): the issues whose corrected test script differs from
# the shipped one SelfHeal read get five more reruns with the corrected script as test.py, in
# <model>/_corrected_input/<tag>/rerun_<k>/, under the same adapted configuration, rules, intents and files.
CORRECTED_INPUT = ["ai_4411", "ai_5628", "ai_6510", "crewai_1532", "haystack_8912", "haystack_9523"]


def corrected_test_text(tag):
    for ext in ("py", "js"):
        p = os.path.join(ROOT, "evaluator", tag, f"reproduce.{ext}")
        if os.path.exists(p):
            return open(p, encoding="utf-8").read()
    raise RuntimeError(f"{tag}: no corrected test script")


def rerun_base(model, tag, corrected):
    return os.path.join(ROOT, model, "_corrected_input", tag) if corrected else os.path.join(ROOT, model, tag)


def build_rerun(model, tag, k, files, how, corrected=False):
    r = os.path.join(rerun_base(model, tag, corrected), f"rerun_{k}")
    fa = os.path.join(r, "Fix-Agent")
    dest = os.path.join(fa, "Dataset-Benchmark", tag)
    os.makedirs(dest, exist_ok=True)
    os.makedirs(os.path.join(fa, "results"), exist_ok=True)
    text, not_utf8 = joined_text(tag, files)
    open(os.path.join(dest, "run_buggy.py"), "w", encoding="utf-8").write(text)
    open(os.path.join(dest, "test.py"), "w", encoding="utf-8").write(corrected_test_text(tag) if corrected else test_text(tag))
    rules_dir = os.path.join(ROOT, model, "rules")
    shutil.copy(os.path.join(rules_dir, "fix_pattern_rules.csv"), os.path.join(fa, "fix_pattern_summaries.csv"))
    rows = [row for row in csv.DictReader(open(os.path.join(rules_dir, "test_descriptions_with_intent.csv"),
                                               encoding="utf-8")) if row["id"] == tag]
    if len(rows) != 1:
        raise RuntimeError(f"{tag}: {len(rows)} intent rows")
    with open(os.path.join(fa, "test_descriptions_with_intent.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "intent"])
        w.writeheader()
        w.writerow({"id": tag, "intent": rows[0]["intent"]})
    shutil.copy(AGENT_FILE, os.path.join(r, "run_agent.py"))
    json.dump({"files": files, "how": how, "not_utf8": not_utf8, "chars": len(text), "configuration": CONFIGURATION,
               "test_input": "corrected" if corrected else "shipped"},
              open(os.path.join(r, "input_files.json"), "w"), indent=1)
    return r


def run_rerun(model, tag, k, corrected=False):
    r = os.path.join(rerun_base(model, tag, corrected), f"rerun_{k}")
    if os.path.exists(os.path.join(r, "Fix-Agent", "results", f"{tag}_result.txt")):
        return tag, k, "done before"
    files, how = input_files(model, tag)
    if not files:
        os.makedirs(r, exist_ok=True)
        json.dump({"no_input": True, "how": how}, open(os.path.join(r, "no_input.json"), "w"), indent=1)
        return tag, k, f"no input file ({how})"
    r = build_rerun(model, tag, k, files, how, corrected)
    rec = ad.run_step(model, r, ad.PY_NEW, "run_agent.py", "run_agent")
    rec["provider"] = PROVIDER
    ad.save_record(os.path.join(r, "run_record.json"), rec)
    return tag, k, rec["exit"]


def repair(model, reruns, parallel, tags, skip=(), corrected=False):
    # skip lists TAG:K reruns still running under another process, so this run does not start them twice.
    tags = tags or (CORRECTED_INPUT if corrected else tags_all())
    jobs = [(t, k) for k in range(1, reruns + 1) for t in tags if f"{t}:{k}" not in skip]
    for s in skip:
        print(s, "skipped, still running under another process", flush=True)
    with ThreadPoolExecutor(parallel) as ex:
        for tag, k, status in ex.map(lambda j: run_rerun(model, *j, corrected=corrected), jobs):
            print(tag, k, status, flush=True)


def redo(model, parallel):
    moved = []
    for tag in tags_all():
        for k in range(1, 6):
            r = os.path.join(ROOT, model, tag, f"rerun_{k}")
            if not os.path.isdir(r) or os.path.exists(os.path.join(r, "no_input.json")):
                continue
            stopped = not os.path.exists(os.path.join(r, "Fix-Agent", "results", f"{tag}_result.txt"))
            where = "_stopped" if stopped else ("_search_failed" if move_aside.search_failed(r) else None)
            if where is None:
                continue
            done_once = any(os.path.exists(os.path.join(ROOT, model, w, tag, f"rerun_{k}"))
                            for w in ("_stopped", "_search_failed"))
            if done_once:
                json.dump({"second": where}, open(os.path.join(r, "redo_second.json"), "w"))
                print(tag, k, where, "again after one redo, kept", flush=True)
                continue
            dest = os.path.join(ROOT, model, where, tag, f"rerun_{k}")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.move(r, dest)
            moved.append((tag, k))
            print(tag, k, "moved to", where, flush=True)
    with ThreadPoolExecutor(parallel) as ex:
        for tag, k, status in ex.map(lambda j: run_rerun(model, *j), moved):
            print(tag, k, "redo", status, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["rules", "pick", "repair", "redo"])
    ap.add_argument("--model", required=True, choices=MODELS)
    ap.add_argument("--reruns", type=int, default=5)
    ap.add_argument("--parallel", type=int, default=5)
    ap.add_argument("--tags", nargs="*")
    ap.add_argument("--provider", choices=["arc", "openrouter"], default="arc")
    ap.add_argument("--skip", nargs="*", default=[])
    ap.add_argument("--corrected-input", action="store_true")    # fix plan departure 14, repair only
    a = ap.parse_args()
    if a.provider == "openrouter":
        use_openrouter(a.model)
    if a.what == "rules":
        ad.rules(a.model)
    elif a.what == "pick":
        pick(a.model)
    elif a.what == "repair":
        repair(a.model, a.reruns, a.parallel, a.tags, a.skip, a.corrected_input)
    else:
        redo(a.model, a.parallel)


if __name__ == "__main__":
    main()
