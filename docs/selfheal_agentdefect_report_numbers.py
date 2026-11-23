"""Compute every number of docs/selfheal_agentdefect_report.md from the AgentDefect records and write the
registry docs/selfheal_agentdefect_report_numbers.md (the number-check skill, section 0).
Reads records only. It writes nothing outside these two docs files.

The calibration groups and the cause of each run follow analyze_multifile.py of the AgentIssue-Bench code,
applied to the AgentDefect records. The unrepaired control is the archive's run_buggy.py and the fix is the
archive's run_fixed.py, each run five times with the case's test.py (AgentDefect/case_check/<model>/<case>/
buggy_<k>/ and fixed_<k>/). A source file follows analyze_multifile.py's patterns. The fix of a case touches
one source file, the program, when run_fixed.py differs from run_buggy.py, and none otherwise. SelfHeal
receives the whole program, so it receives every file the fix touches.

  python docs/selfheal_agentdefect_report_numbers.py
"""
import collections
import csv
import datetime
import glob
import json
import os
import re
import statistics
import zipfile

H = "/data/wang/junh/githubs/stochastic-harness"
AD = f"{H}/AgentDefect/SelfHeal"
CHECK = f"{H}/AgentDefect/case_check"
SH = "/data/wang/junh/githubs/SelfHeal"
ZIP = f"{SH}/AgentDefect.zip"
LG = "/data/wang/junh/envs/selfheal/lib/python3.10/site-packages/langgraph/_internal/_config.py"
M = "gpt-oss-120b"
MODELS = ["gpt-oss-120b", "DeepSeek-V4.1-Flash", "GLM-5.3"]
OUT = f"{H}/docs/selfheal_agentdefect_report_numbers.md"
today = datetime.date.today().isoformat()
rows = []

# the rules of analyze_multifile.py (AgentIssue-Bench/SelfHeal/code/analyze_multifile.py lines 42 to 47 and 82 to 92)
APPLY_FAIL = re.compile(r"Failed to apply patch|Hunk #\d+ FAILED|can't find file to patch|No file to patch|malformed patch|patch: \*\*\*\*")
NO_PATCH_PROGRAM = re.compile(r"patch: command not found|patch: not found")
FAILURE_LINE = re.compile(r"error|exception|fail|❌|traceback|assert|not verified|not confirmed|bug reproduced", re.I)


def add(name, value, what, source, how):
    rows.append((name, str(value), what, source, how))


def r2(x):
    return f"{x:.2f}"


def r3(x):
    return f"{x:.3f}"


def line_of(path, n, must):
    text = open(path, encoding="utf-8").read().splitlines()[n - 1]
    assert must in text, (path, n, text)
    return n


def read(path):
    return open(path, encoding="utf-8", errors="replace").read() if os.path.exists(path) else ""


def last_failure_line(folder):
    for name in ("test.log", "test_stderr.log"):
        lines = [l.strip() for l in read(os.path.join(folder, name)).splitlines() if l.strip()]
        hits = [l for l in lines if FAILURE_LINE.search(l)]
        if hits:
            l = hits[-1].lower()
            l = re.sub(r"0x[0-9a-f]+|\b[0-9a-f]{7,}\b", "H", l)
            l = re.sub(r"/[\w.\-/]+", "P", l)
            l = re.sub(r"\d+", "N", l)
            return re.sub(r"\s+", " ", l)
    return None


def archive_text(case, name):
    if case == "hf-26" and name == "run_buggy.py":   # the rebuilt buggy program, AgentDefect/SelfHeal/inputs
        return open(f"{AD}/inputs/hf-26_run_buggy.py", encoding="utf-8").read()
    z = zipfile.ZipFile(ZIP)
    p = [q for q in z.namelist() if not q.startswith("__MACOSX") and q.split("/")[1:] == [case, name]][0]
    return z.read(p).decode("utf-8")


# code locations cited in the report
add("code_attempt_loop", line_of(f"{SH}/run_agent.py", 281, "max_attempts: int = 3"), "line that sets three attempts",
    "/data/wang/junh/githubs/SelfHeal/run_agent.py", "line text")
add("code_verify_first", 204, "first docstring line of verify_api_usage, the critic's search tool", "/data/wang/junh/githubs/SelfHeal/run_agent.py", "line text")
assert "Searches the internet" in open(f"{SH}/run_agent.py").read().splitlines()[203]
add("code_verify_last", line_of(f"{SH}/run_agent.py", 229, "Verification results for"), "last line of verify_api_usage", "/data/wang/junh/githubs/SelfHeal/run_agent.py", "line text")
add("code_fixer_tools_first", line_of(f"{SH}/run_agent.py", 247, "tools = ["), "first line of the fix agent's tool list", "/data/wang/junh/githubs/SelfHeal/run_agent.py", "line text")
add("code_fixer_agent", line_of(f"{SH}/run_agent.py", 254, "create_react_agent(llm, tools)"), "line that builds the fix agent", "/data/wang/junh/githubs/SelfHeal/run_agent.py", "line text")
add("code_fixer_stream_first", line_of(f"{SH}/run_agent.py", 325, "fixer.stream("), "first line of the fix agent's run call", "/data/wang/junh/githubs/SelfHeal/run_agent.py", "line text")
add("code_fixer_stream_last", line_of(f"{SH}/run_agent.py", 328, "):"), "last line of the fix agent's run call", "/data/wang/junh/githubs/SelfHeal/run_agent.py", "line text")
add("code_success_line", line_of(f"{AD}/code/score_tests.py", 143, '"final_success": ks == "ACCEPTED" and kt["passed"]'),
    "line of AgentDefect score_tests.py that defines a success", "AgentDefect/SelfHeal/code/score_tests.py", "line text")
lg = open(LG).read().splitlines()
add("langgraph_limit_line", 31, "line of langgraph's _config.py that sets the default step limit", LG, "line text")
add("langgraph_default_limit", re.search(r'"(\d+)"', lg[30]).group(1), "langgraph 1.1.6 default recursion limit", LG, "value on line 31")

# setup table
fr = json.load(open(f"{AD}/inputs/fetch_record.json"))
add("setup_cases", fr["case_folders"], "AgentDefect case folders", "AgentDefect/SelfHeal/inputs/fetch_record.json", "case_folders")
add("setup_train_posts", fr["train_ids"], "training posts the fix rules need", "AgentDefect/SelfHeal/inputs/fetch_record.json", "train_ids")
add("setup_train_returned", fr["train_ids"] - len(fr["train_missing"]), "training posts the Stack Exchange API returned", "AgentDefect/SelfHeal/inputs/fetch_record.json", "train_ids minus the length of train_missing")
for k, m in enumerate(fr["train_missing"], 1):
    add(f"setup_missing_post_{k}", m, "id of a training post the Stack Exchange API did not return", "AgentDefect/SelfHeal/inputs/fetch_record.json", "train_missing")
add("setup_train_missing", len(fr["train_missing"]), "training posts the API did not return", "AgentDefect/SelfHeal/inputs/fetch_record.json", "train_missing")
with open(f"{AD}/{M}/rules/fix_pattern_rules.csv", newline="") as fh:
    add("setup_rules", len(list(csv.DictReader(fh))), "fix rules built by SelfHeal's scripts", f"AgentDefect/SelfHeal/{M}/rules/fix_pattern_rules.csv", "data rows")
add("setup_paper_patterns", 23, "fix patterns the SelfHeal paper states", "SelfHeal paper arXiv 2604.17699 v1, section 3", 'text "twenty-three fix patterns"')
lists = sorted({os.path.basename(p)[:-len("_install.json")] for p in glob.glob(f"{AD}/test_env_logs/list_*_install.json")})
base = [l for l in lists if re.fullmatch(r"list_\d+", l)]
add("setup_req_lists", len(base), "distinct requirement lists over the cases", "AgentDefect/SelfHeal/test_env_logs/list_<n>_install.json", "list_<n> records without a letter suffix")
add("setup_arc_cap", 8000, "token cap ARC sets on replies that are not streamed", "docs/selfheal_deployment.md section 2.2", "observed when GLM-5.3 replies stopped at the cap before the relay streamed")

# success and the four outcomes, the score tables' cases
T = [r for r in csv.DictReader(open(f"{AD}/test_scores.csv")) if r["model"] == M]
S = [r for r in T if r["in_table"] == "True"]
cases = sorted({r["case"] for r in S})
dropped = sorted({r["case"] for r in T} - set(cases))
add("ad_cases_scored", len(cases), "cases in the score tables", "AgentDefect/SelfHeal/test_scores.csv", "distinct case with in_table True")
add("ad_runs", len(S), "gpt-oss-120b planned repetitions in the score tables, five per case", "AgentDefect/SelfHeal/test_scores.csv", "in_table rows of gpt-oss-120b")
assert dropped == ["79776520"], dropped
add("ad_dropped_case", dropped[0], "case left out of the score tables, needs Google and Tavily keys", "AgentDefect/SelfHeal/test_scores.csv", "case with in_table False")
succ = sum(r["final_success"] == "True" for r in S)
add("ad_successes", succ, "runs ACCEPTED whose repair passed test.py", "AgentDefect/SelfHeal/test_scores.csv", "final_success True")
per = collections.Counter()
for r in S:
    per[r["case"]] += r["final_success"] == "True"
dist = collections.Counter(per[c] for c in cases)
for k in range(6):
    add(f"ad_cases_with_{k}", dist[k], f"cases with {k} successful runs of five", "AgentDefect/SelfHeal/test_scores.csv", "successes per case")
four = collections.Counter((r["final_status"], r["final_test_passed"]) for r in S)
for (s, p), v in [(("ACCEPTED", "True"), "accepted_pass"), (("ACCEPTED", "False"), "accepted_fail"), (("FAILED", "True"), "failed_pass"),
                  (("FAILED", "False"), "failed_fail"), (("NO RESULT", "False"), "no_result")]:
    add(f"ad_{v}", four[(s, p)], f"runs with status {s} and test passed {p}", "AgentDefect/SelfHeal/test_scores.csv", "final_status, final_test_passed")
assert sum(four.values()) == len(S), four
add("ad_test_passed", four[("ACCEPTED", "True")] + four[("FAILED", "True")], "runs whose final code passed test.py, either status",
    "AgentDefect/SelfHeal/test_scores.csv", "final_test_passed True")


# groups from the original program's five runs and the cause of each run, the rules of analyze_multifile.py on
# the AgentDefect records. The runs of the authors' fixed program are dropped (plan step 3k), so the groups use
# the original program only: passes without a fix, fails without a fix, unstable.
def calibration(case):
    neg = [json.load(open(p))["passed"] for p in sorted(glob.glob(f"{CHECK}/{M}/{case}/buggy_*/test_record.json"))]
    assert len(neg) == 5, (case, len(neg))
    nulls = {last_failure_line(os.path.dirname(p)) for p in glob.glob(f"{CHECK}/{M}/{case}/buggy_*/test_record.json")}
    if all(neg):
        return "passes without a fix", nulls
    if not any(neg):
        return "fails without a fix", nulls
    return "unstable", nulls


A = []
for c in cases:
    group, nulls = calibration(c)
    fix_changes = archive_text(c, "run_fixed.py") != archive_text(c, "run_buggy.py")
    fg = "one" if fix_changes else "none"
    for r in [x for x in S if x["case"] == c]:
        d = f"{AD}/{M}/{c}/rerun_{r['rerun']}"
        status = r["final_status"]
        rp = f"{d}/test/test_record.json"
        rec = json.load(open(rp)) if os.path.exists(rp) else None
        passed = bool(rec and rec.get("passed"))
        note = str((rec or {}).get("split_note") or (rec or {}).get("not_run") or "")
        left_out = note.startswith("header missing") or note.startswith("several files sent")
        log = read(f"{d}/test/test.log") + read(f"{d}/test/test_stderr.log")
        not_applied = bool(APPLY_FAIL.search(log)) or bool(NO_PATCH_PROGRAM.search(log))
        changed = 0 if r["final_changed_functions"].strip() in ("", "none") else 1   # score_tests.py writes "none" for an unchanged program
        need = 1 if fg == "one" else 0
        got_all = "n/a" if fg == "none" else "yes"
        if status == "NO RESULT" or rec is None or (rec.get("not_run") and not left_out):
            cause = "no repair"
        elif group == "passes without a fix":
            cause = "test passes without a fix"
        elif group == "unstable":
            cause = "test unstable"
        elif passed:
            cause = "test passed"
        elif got_all == "no":
            cause = "did not get every file the fix touches"
        elif left_out:
            cause = "left out a file it got"
        elif not_applied:
            cause = "patch did not apply"
        elif fg == "one" and changed < need:
            cause = "changed fewer source files than the fix"
        elif last_failure_line(f"{d}/test") in nulls:
            cause = "failed like the null patch"
        else:
            cause = "failed otherwise"
        A.append(dict(case=c, rerun=r["rerun"], group=group, fix_group=fg, got_all=got_all, status=status, passed=passed,
                      cause=cause, success=r["final_success"] == "True"))
assert len(A) == len(S)
gi = collections.defaultdict(set)
for r in A:
    gi[r["group"]].add(r["case"])
GROUPS = [("fails without a fix", "fail"), ("passes without a fix", "null"), ("unstable", "mixed")]
for g, k in GROUPS:
    G = [r for r in A if r["group"] == g]
    add(f"grp_{k}_issues", len(gi[g]), f"cases whose original program gives the group '{g}'", "AgentDefect/case_check/gpt-oss-120b/<case>/buggy_<k>", "five runs of the original program")
    add(f"grp_{k}_runs", len(G), f"runs in cases of the group '{g}'", "AgentDefect/SelfHeal/test_scores.csv", "rows per group")
    cc = collections.Counter((r["status"], r["passed"]) for r in G)
    for (s, p), v in [(("ACCEPTED", True), "ap"), (("ACCEPTED", False), "af"), (("FAILED", True), "fp"), (("FAILED", False), "ff"), (("NO RESULT", False), "nr")]:
        add(f"grp_{k}_{v}", cc[(s, p)], f"runs of group '{g}' with status {s} and test passed {p}", "AgentDefect/SelfHeal/test_scores.csv", "final_status, final_test_passed")
assert sum(len(v) for v in gi.values()) == len(cases)
CAUSES = ["no repair", "test passes without a fix", "test unstable", "test passed",
          "did not get every file the fix touches", "left out a file it got", "patch did not apply",
          "changed fewer source files than the fix", "failed like the null patch", "failed otherwise"]
cc = collections.Counter(r["cause"] for r in A)
assert set(cc) <= set(CAUSES) and sum(cc.values()) == len(A)
for i, c in enumerate(CAUSES):
    for s, v in [(None, "runs"), ("ACCEPTED", "acc"), ("FAILED", "fail"), ("NO RESULT", "nores")]:
        n = sum(r["cause"] == c and (s is None or r["status"] == s) for r in A)
        add(f"cause{i}_{v}", n, f"runs with cause '{c}'" + (f", status {s}" if s else ""), "AgentDefect records, rules of analyze_multifile.py", "cause, status")
sep = [r for r in A if r["group"] == "fails without a fix"]
sep_cases = gi["fails without a fix"]
add("sep_failures", sum(not r["passed"] and r["cause"] != "no repair" for r in sep), "failing runs with a repair in cases that fail without a fix", "AgentDefect records", "cause other than test passed and no repair")
add("sep_accepted", sum(r["status"] == "ACCEPTED" for r in sep), "runs ACCEPTED in cases that fail without a fix", "AgentDefect/SelfHeal/test_scores.csv", "final_status")
add("sep_rejected", sum(r["status"] == "FAILED" for r in sep), "runs FAILED in cases that fail without a fix", "AgentDefect/SelfHeal/test_scores.csv", "final_status")
add("sep_successes", sum(r["success"] for r in sep), "successes in cases that fail without a fix", "AgentDefect/SelfHeal/test_scores.csv", "final_success")
add("null_successes", sum(r["success"] for r in A if r["group"] == "passes without a fix"), "successes in cases that pass without a fix", "AgentDefect/SelfHeal/test_scores.csv", "final_success")
add("mixed_successes", sum(r["success"] for r in A if r["group"] == "unstable"), "successes in unstable cases", "AgentDefect/SelfHeal/test_scores.csv", "final_success")
for fg in ["one", "two to seven", "unknown", "none"]:
    F = [r for r in sep if r["fix_group"] == fg]
    k = fg.replace(" ", "_")
    add(f"fix_{k}_issues", len({r['case'] for r in F}), f"cases that fail without a fix whose fix touches '{fg}' source files", "AgentDefect.zip run_buggy.py and run_fixed.py", "text differs")
    add(f"fix_{k}_runs", len(F), "runs of those cases", "AgentDefect/SelfHeal/test_scores.csv", "rows")
    add(f"fix_{k}_got", sum(r["got_all"] == "yes" for r in F), "of those runs, SelfHeal received every fix file", "AgentDefect records", "the whole program is SelfHeal's input")
    add(f"fix_{k}_passed", sum(r["passed"] for r in F), "of those runs, test.py passed", "AgentDefect/SelfHeal/<model>/<case>/rerun_<k>/test/test_record.json", "passed")

# what each repair changed against the functions the fixed program changes, cases that fail without a fix.
# The units are those of AgentDefect score_tests.py code_units: each top-level function, each class method,
# each class body and the module-level code. The repair's units are the final_changed_functions column.
st = open(f"{AD}/code/score_tests.py").read()
nsu = {"ast": __import__("ast")}
exec(st[st.index("def code_units"):st.index("def changed_functions")], nsu)
code_units = nsu["code_units"]


def unit_diff(old, new):
    o, n = code_units(old), code_units(new)
    return {x for x in set(o) & set(n) if o[x] != n[x]} | (set(n) - set(o)) | (set(o) - set(n))


CH = collections.Counter()
for c in sorted(sep_cases):
    fu = unit_diff(archive_text(c, "run_buggy.py"), archive_text(c, "run_fixed.py"))
    for r in [x for x in S if x["case"] == c]:
        v = r["final_changed_functions"].strip()
        if v in ("no repair file", "repair does not parse"):
            k = "unknown"
        else:
            ru = set() if v in ("", "none") else {u.replace(" added", "").replace(" removed", "") for u in v.split("; ")}
            k = "no_fix_units" if not fu else "every" if fu <= ru else "some" if fu & ru else "none"
        CH[(k, "runs")] += 1; CH[(k, "passed")] += r["final_test_passed"] == "True"; CH[(k, "succ")] += r["final_success"] == "True"
        CH[(k, "cases", c)] = 1
src = "AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions"
for k in ["every", "some", "none", "no_fix_units", "unknown"]:
    add(f"chf_{k}_cases", sum(1 for key in CH if key[0] == k and key[1] == "cases"), f"cases that fail without a fix with a run whose repair changed '{k}' of the fix's functions", src, "code_units of score_tests.py")
    add(f"chf_{k}_runs", CH[(k, "runs")], f"runs whose repair changed '{k}' of the functions the fixed program changes", src, "code_units of score_tests.py")
    add(f"chf_{k}_passed", CH[(k, "passed")], "of those runs, test passed", src, "final_test_passed")
    add(f"chf_{k}_succ", CH[(k, "succ")], "of those runs, successes", src, "final_success")
assert sum(CH[(k, "runs")] for k in ["every", "some", "none", "no_fix_units", "unknown"]) == len(sep)

# the worked example of the three sets, case 77099194: rows retrieved and test results
EX = "77099194"
add("ex_case", EX, "case used as the worked example of the three sets", "AgentDefect.zip", "case folder name")
kre = re.compile(r'search_kwargs=\{"k":\s*(\w+)\}')
add("ex_k_buggy", kre.search(archive_text(EX, "run_buggy.py")).group(1), "rows the buggy program retrieves", "AgentDefect.zip run_buggy.py", "search_kwargs k")
add("ex_k_fixed", kre.search(archive_text(EX, "run_fixed.py")).group(1), "rows the authors' fixed program retrieves", "AgentDefect.zip run_fixed.py", "search_kwargs k")
for prog in ("buggy",):
    ps = [json.load(open(q))["passed"] for q in sorted(glob.glob(f"{CHECK}/{M}/{EX}/{prog}_*/test_record.json"))]
    add(f"ex_{prog}_runs", len(ps), f"calibration runs of the {prog} program for the example case", f"AgentDefect/case_check/{M}/{EX}/{prog}_<k>/test_record.json", "count")
    add(f"ex_{prog}_passed", sum(ps), f"of those, passed", f"AgentDefect/case_check/{M}/{EX}/{prog}_<k>/test_record.json", "passed")
EXL = []
for r in sorted([x for x in S if x["case"] == EX], key=lambda x: int(x["rerun"])):
    code = open(f"{AD}/{M}/{EX}/rerun_{r['rerun']}/test/run_fixed.py").read()
    m = kre.search(code); kv = m.group(1)
    if not kv.isdigit():   # the repair passes k as a parameter, read its default
        kv = re.search(r"\b" + kv + r"\s*:\s*int\s*=\s*(\d+)", code).group(1)
    nlines = sum(1 for l in __import__("difflib").unified_diff(archive_text(EX, "run_buggy.py").splitlines(), code.splitlines(), n=0)
                 if l[:1] in "+-" and not l.startswith(("+++", "---")))
    add(f"ex_rep{r['rerun']}_lines", nlines, f"lines repair {r['rerun']} adds or removes against the buggy program", f"AgentDefect/SelfHeal/{M}/{EX}/rerun_{r['rerun']}/test/run_fixed.py", "unified diff, zero context")
    EXL.append(nlines)
    add(f"ex_rep{r['rerun']}_k", kv, f"rows repair {r['rerun']} retrieves", f"AgentDefect/SelfHeal/{M}/{EX}/rerun_{r['rerun']}/test/run_fixed.py", "search_kwargs k or its default")
    add(f"ex_rep{r['rerun']}_status", r["final_status"], f"critic's final verdict on repair {r['rerun']}", "AgentDefect/SelfHeal/test_scores.csv", "final_status")
    add(f"ex_rep{r['rerun']}_passed", int(r["final_test_passed"] == "True"), f"repair {r['rerun']} passed the test", "AgentDefect/SelfHeal/test_scores.csv", "final_test_passed")

assert all(35 <= x <= 45 for x in EXL), EXL
add("ex_lines_about", 40, "lines each repair changed, rounded, the five repairs changed 39 to 43", "AgentDefect/SelfHeal/gpt-oss-120b/77099194/rerun_<k>/test/run_fixed.py", "ex_rep<k>_lines, all within 35 to 45")

# the critic's first verdict, from SelfHeal's result files
att = []
for r in S:
    f = glob.glob(f"{AD}/{M}/{r['case']}/rerun_{r['rerun']}/Fix-Agent/results/*_result.txt")
    if not f:
        continue
    t = open(f[0]).read()
    att.append(dict(case=r["case"], status=re.search(r"(?m)^Status: (\w+)", t).group(1), final=int(re.search(r"(?m)^Final Attempt: (\d+)", t).group(1)),
                    durs=[float(x) for x in re.findall(r"(?m)^Duration: ([\d.]+) seconds", t)], success=r["final_success"] == "True"))
for lab, sel in [("fail", [a for a in att if a["case"] in sep_cases]), ("all", att)]:
    acc1 = [a for a in sel if a["status"] == "ACCEPTED" and a["final"] == 1]
    rej1 = [a for a in sel if not (a["status"] == "ACCEPTED" and a["final"] == 1)]
    share = sum(a["durs"][0] for a in sel) / sum(sum(a["durs"]) for a in sel)
    src, how = "AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt", "Status, Final Attempt, Duration lines"
    add(f"v1_{lab}_runs", len(sel), f"runs with a result file, {lab} cases", src, how)
    add(f"v1_{lab}_acc1", len(acc1), "runs ACCEPTED at attempt 1", src, how)
    add(f"v1_{lab}_acc1_succ", sum(a["success"] for a in acc1), "successes among them", src, how + ", final_success of test_scores.csv")
    add(f"v1_{lab}_rej1", len(rej1), "runs rejected at attempt 1", src, how)
    add(f"v1_{lab}_rej1_succ", sum(a["success"] for a in rej1), "successes among them", src, how + ", final_success of test_scores.csv")
    add(f"v1_{lab}_share", r2(share), "attempt 1 duration over all attempts' duration, summed over runs", src, how)
    add(f"v1_{lab}_after", r2(1 - share), "attempts 2 and 3 duration over all attempts' duration", src, how)
    acc = [a for a in sel if a["status"] == "ACCEPTED"]
    add(f"v1_{lab}_acc_any", len(acc), "runs ACCEPTED at any attempt", src, how)
    add(f"v1_{lab}_rejected", len(sel) - len(acc), "runs FAILED, rejected at every attempt", src, how)
    for k in (1, 2, 3):
        add(f"v1_{lab}_stop{k}", sum(a["success"] for a in sel if a["status"] == "ACCEPTED" and a["final"] <= k),
            f"successes if SelfHeal stopped after attempt {k}", src, how)
    add(f"v1_{lab}_rej1_acc_at2", sum(a["status"] == "ACCEPTED" and a["final"] == 2 and a["success"] for a in rej1), "successes accepted at attempt 2", src, how)

# test share of time
for lab, keep in [("fail", lambda c: c in sep_cases), ("all", lambda c: True)]:
    rep = tst = n = 0
    for r in S:
        if not keep(r["case"]):
            continue
        d = f"{AD}/{M}/{r['case']}/rerun_{r['rerun']}"
        if not (os.path.exists(f"{d}/run_record.json") and os.path.exists(f"{d}/test/test_record.json")):
            continue
        rr, tr = json.load(open(f"{d}/run_record.json")), json.load(open(f"{d}/test/test_record.json"))
        if "seconds" not in tr:
            continue
        rep += sum(a["seconds"] for a in rr["attempts"]); tst += tr["seconds"]; n += 1
    src = "AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/run_record.json and test/test_record.json"
    add(f"ts_{lab}_runs", n, f"runs with both a repair time and a test time, {lab} cases", src, "both files present, test record has seconds")
    add(f"ts_{lab}_repair_h", r2(rep / 3600), "repair hours", src, "sum of run_record attempts seconds / 3600")
    add(f"ts_{lab}_repair_min_run", r2(rep / 60 / n), "SelfHeal minutes per run", src, "sum of run_record attempts seconds / 60 / runs")
    add(f"ts_{lab}_test_min_run", r2(tst / 60 / n), "test minutes per run", src, "sum of test_record seconds / 60 / runs")
    add(f"ts_{lab}_test_h", r2(tst / 3600), "test hours", src, "sum of test_record seconds / 3600")
    add(f"ts_{lab}_share", r3(tst / (rep + tst)), "test share of repair plus test time", src, "test / (repair + test)")

# web search, three models, the fix agent's web_search and the critic's verify_api_usage, streamed configuration only
TOOLS = {"web_search", "verify_api_usage"}
errtext = collections.Counter()
for m in MODELS:
    logs = [p for p in glob.glob(f"{AD}/{m}/**/relay_log_run_agent.jsonl", recursive=True) if "/_not_streamed/" not in p]
    runs = {}
    for log in logs:
        calls, seen, n, e = {}, set(), 0, 0
        for line in open(log, encoding="utf-8"):
            for msg in json.loads(line)["request"].get("messages", []):
                if msg.get("role") == "assistant":
                    for c in msg.get("tool_calls") or []:
                        if c["function"]["name"] in TOOLS:
                            calls[c["id"]] = 1
                elif msg.get("role") == "tool" and msg.get("tool_call_id") in calls and msg["tool_call_id"] not in seen:
                    seen.add(msg["tool_call_id"]); body = str(msg.get("content")); n += 1
                    if "Search error" in body:
                        e += 1
                        errtext["ddg_timeout" if ("html.duckduckgo.com" in body and "timed out" in body) else "other"] += 1
        if n:
            runs[log] = (n, e)
    N = sum(v[0] for v in runs.values()); E = sum(v[1] for v in runs.values()); p = E / N
    k = m.split("-")[0].lower()
    src, how = f"AgentDefect/SelfHeal/{m}/**/relay_log_run_agent.jsonl without _not_streamed", "web_search and verify_api_usage tool replies, kept and moved-aside runs"
    add(f"s_{k}_searches", N, f"{m} searches", src, how)
    add(f"s_{k}_fail", r3(p), f"{m} share of searches with 'Search error'", src, how)
    add(f"s_{k}_median", (lambda x: int(x) if x == int(x) else x)(statistics.median(v[0] for v in runs.values())), f"{m} median searches per run with a search", src, how)
    add(f"s_{k}_max", max(v[0] for v in runs.values()), f"{m} most searches in one run", src, how)
    add(f"s_{k}_runs_err", r2(sum(v[1] > 0 for v in runs.values()) / len(runs)), f"{m} share of runs with a failed search", src, how)
    add(f"s_{k}_expected", r2(statistics.mean(1 - (1 - p) ** v[0] for v in runs.values())),
        f"{m} share expected if each search fails independently at the model's rate", src, "mean over runs of 1-(1-p)^n")
add("s_errors_all", sum(errtext.values()), "search errors over the three models", "relay logs of the three models", "replies with 'Search error'")
add("s_errors_ddg", errtext["ddg_timeout"], "of those, a timeout on html.duckduckgo.com", "relay logs of the three models", "reply text")

with open(OUT, "w") as f:
    f.write("# Number registry, SelfHeal on AgentDefect\n\n")
    f.write("Rows written by `docs/selfheal_agentdefect_report_numbers.py`. The report is checked with\n\n")
    f.write("```\npython3 ~/.claude/skills/number-check/scripts/check_numbers.py --registry docs/selfheal_agentdefect_report_numbers.md "
            "--ignore '^[0-9]\\.[0-9](\\.[0-9])?$' --ignore '^(2611\\.09792|1603\\.09326|2604\\.17699)$' docs/selfheal_agentdefect_report.md\n```\n\n")
    f.write("The ignore patterns skip section numbers and the three arXiv ids.\n\n")
    f.write("| name | value | what it counts | source file | how it is computed | date read |\n|---|---|---|---|---|---|\n")
    for r in rows:
        f.write("| " + " | ".join(r) + f" | {today} |\n")
print(len(rows), "rows written to", OUT)
for r in rows:
    print(r[0], r[1])
