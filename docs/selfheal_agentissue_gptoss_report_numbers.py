"""Compute every number of docs/selfheal_agentissue_gptoss_report.md from its source files and write the
registry docs/selfheal_agentissue_gptoss_report_numbers.md (the number-check skill, section 0).
Reads records only. It writes nothing outside these two docs files.

  python docs/selfheal_agentissue_gptoss_report_numbers.py
"""
import collections
import csv
import datetime
import glob
import json
import os
import re
import statistics

H = "/data/wang/junh/githubs/stochastic-harness"
AI = f"{H}/AgentIssue-Bench/SelfHeal"
SH = "/data/wang/junh/githubs/SelfHeal"
LG = "/data/wang/junh/envs/selfheal/lib/python3.10/site-packages/langgraph/_internal/_config.py"
M = "gpt-oss-120b"
MODELS = ["gpt-oss-120b", "DeepSeek-V4.1-Flash", "GLM-5.3"]
OUT = f"{H}/docs/selfheal_agentissue_gptoss_report_numbers.md"
today = datetime.date.today().isoformat()
rows = []


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


# code locations cited in the report, each checked against the line's text
add("code_final_success_line", line_of(f"{AI}/code/score_tests.py", 107, '"final_success": ks == "ACCEPTED" and kr["passed"]'),
    "line of score_tests.py that defines a success", "AgentIssue-Bench/SelfHeal/code/score_tests.py", "line text holds the final_success rule")
add("code_fixer_tools_first", line_of(f"{SH}/run_agent.py", 247, "tools = ["), "first line of the fix agent's tool list",
    "/data/wang/junh/githubs/SelfHeal/run_agent.py", "line text")
add("code_fixer_agent", line_of(f"{SH}/run_agent.py", 254, "create_react_agent(llm, tools)"), "line that builds the fix agent",
    "/data/wang/junh/githubs/SelfHeal/run_agent.py", "line text")
add("code_fixer_stream_first", line_of(f"{SH}/run_agent.py", 325, "fixer.stream("), "first line of the fix agent's run call",
    "/data/wang/junh/githubs/SelfHeal/run_agent.py", "line text")
add("code_fixer_stream_last", line_of(f"{SH}/run_agent.py", 328, "):"), "last line of the fix agent's run call",
    "/data/wang/junh/githubs/SelfHeal/run_agent.py", "line text")
add("code_verify_first", 204, "first docstring line of verify_api_usage, the critic's search tool",
    "/data/wang/junh/githubs/SelfHeal/run_agent.py", "line text")
assert "Searches the internet" in open(f"{SH}/run_agent.py").read().splitlines()[203]
add("code_verify_last", line_of(f"{SH}/run_agent.py", 229, "Verification results for"), "last line of verify_api_usage",
    "/data/wang/junh/githubs/SelfHeal/run_agent.py", "line text")
add("code_attempt_loop", line_of(f"{SH}/run_agent.py", 281, "max_attempts: int = 3"), "line that sets three attempts",
    "/data/wang/junh/githubs/SelfHeal/run_agent.py", "line text")
# setup table, counts and settings checked against their sources
named = json.load(open(f"{AI}/inputs/named_files.json"))
n_named = sum(1 for v in named.values() if (v if isinstance(v, list) else v.get("files", [])))
add("setup_named_issues", n_named, "issues whose report names at least one repository file", "AgentIssue-Bench/SelfHeal/inputs/named_files.json", "issues with a non-empty file list")
add("setup_picked_issues", len(named) - n_named, "issues whose files the run's model picks", "AgentIssue-Bench/SelfHeal/inputs/named_files.json", "issues with an empty file list")
add("setup_arm64_rebuilt", len(glob.glob(f"{H}/AgentIssue-Bench/images_amd64/*/")), "images built only for arm64 and rebuilt for amd64", "AgentIssue-Bench/images_amd64/", "folders, one per rebuilt image")
with open(f"{AI}/{M}/rules/fix_pattern_rules.csv", newline="") as fh:
    add("setup_rules", len(list(csv.DictReader(fh))), "fix rules built by SelfHeal's scripts, one per pattern name", f"AgentIssue-Bench/SelfHeal/{M}/rules/fix_pattern_rules.csv", "data rows")
add("setup_paper_patterns", 23, "fix patterns the SelfHeal paper states", "SelfHeal paper arXiv 2604.17699 v1, section 3", 'text "twenty-three fix patterns"')
add("setup_test_timeout", line_of("/data/wang/junh/githubs/AgentIssue-Bench/eval_patches.py", 112, "timeout=300") and 300,
    "seconds the benchmark allows each test command", "/data/wang/junh/githubs/AgentIssue-Bench/eval_patches.py", "line 112, timeout=300")
add("setup_arc_cap", 8000, "token cap ARC sets on replies that are not streamed", "docs/selfheal_deployment.md section 2.2", "observed when GLM-5.3 replies stopped at the cap before the relay streamed")
add("code_calib_per_model_first", line_of(f"{AI}/code/calibrate.py", 3, "Per issue and model, five runs of each control"),
    "first line of calibrate.py's statement that calibration runs per issue and model", "AgentIssue-Bench/SelfHeal/code/calibrate.py", "line text")
add("code_calib_per_model_last", line_of(f"{AI}/code/calibrate.py", 4, "under the shipped evaluator"),
    "last line of that statement", "AgentIssue-Bench/SelfHeal/code/calibrate.py", "line text")
add("code_arc_again_first", line_of(f"{AI}/code/run_arc_again.sh", 2, "back on ARC"),
    "first line of run_arc_again.sh's statement that DeepSeek-V4.1-Flash moved back to ARC", "AgentIssue-Bench/SelfHeal/code/run_arc_again.sh", "line text")
add("code_arc_again_last", line_of(f"{AI}/code/run_arc_again.sh", 4, 'result are kept ("done before")'),
    "line that keeps reruns with a SelfHeal result from the OpenRouter run", "AgentIssue-Bench/SelfHeal/code/run_arc_again.sh", "line text")
lg = open(LG).read().splitlines()
add("langgraph_limit_line", 31, "line of langgraph's _config.py that sets the default step limit", LG, "line text")
add("langgraph_default_limit", re.search(r'"(\d+)"', lg[30]).group(1), "langgraph 1.1.6 default recursion limit, steps per run call",
    LG, "value on line 31")

# success and the four outcomes, shipped evaluator
tags = sorted(json.load(open(f"{AI}/inputs/named_files.json")))
S = [r for r in csv.DictReader(open(f"{AI}/test_scores.csv")) if r["evaluator"] == "shipped" and r["model"] == M]
add("go_issues", len(tags), "AgentIssue-Bench issues run", "AgentIssue-Bench/SelfHeal/inputs/named_files.json", "keys")
add("go_runs", len(S), "gpt-oss-120b planned repetitions, five per issue", "AgentIssue-Bench/SelfHeal/test_scores.csv", "shipped rows of gpt-oss-120b")
succ = sum(r["final_success"] == "True" for r in S)
add("go_successes", succ, "runs ACCEPTED whose repair passed the shipped test", "AgentIssue-Bench/SelfHeal/test_scores.csv", "final_success True")
per = collections.Counter()
for r in S:
    per[r["tag"]] += r["final_success"] == "True"
dist = collections.Counter(per[t] for t in tags)
for k in range(6):
    add(f"go_issues_with_{k}", dist[k], f"issues with {k} successful runs of five", "AgentIssue-Bench/SelfHeal/test_scores.csv", "successes per tag")
four = collections.Counter((r["final_status"], r["final_test_passed"]) for r in S)
for (s, p), v in [(("ACCEPTED", "True"), "accepted_pass"), (("ACCEPTED", "False"), "accepted_fail"), (("FAILED", "True"), "failed_pass"),
                  (("FAILED", "False"), "failed_fail"), (("NO RESULT", "False"), "no_result")]:
    add(f"go_{v}", four[(s, p)], f"runs with status {s} and shipped test passed {p}", "AgentIssue-Bench/SelfHeal/test_scores.csv", "final_status, final_test_passed")
assert sum(four.values()) == len(S)
add("go_test_passed", four[("ACCEPTED", "True")] + four[("FAILED", "True")], "runs whose final code passed the shipped test, either status",
    "AgentIssue-Bench/SelfHeal/test_scores.csv", "final_test_passed True")

# groups from the original code's five runs (null patch, shipped evaluator) and the cause of each run, with
# analyze_multifile.py's own functions. The runs of the developer's fix are dropped (plan step 3k), so the
# groups use the original code only: passes without a fix, fails without a fix, unstable.
amf_src = open(f"{AI}/code/analyze_multifile.py").read()
nsm = {"__name__": "analyze_multifile"}
exec(compile(amf_src, "analyze_multifile.py", "exec"), nsm)
CHECKD = nsm["CHECK"]


def original_group(tag):
    paths = sorted(glob.glob(os.path.join(CHECKD, M, tag, "shipped_negative_*", "test_record.json")))
    neg = [json.load(open(q))["passed"] for q in paths]
    assert len(neg) == 5, (tag, len(neg))
    nulls = {nsm["last_failure_line"](os.path.dirname(q)) for q in paths}
    if all(neg):
        return "passes without a fix", nulls
    if not any(neg):
        return "fails without a fix", nulls
    return "unstable", nulls


A = []
for t in tags:
    group, nulls = original_group(t)
    need = nsm["fix_files"](t)
    fg = nsm["fix_group"](len(need))
    for k in range(1, 6):
        d = os.path.join(AI, M, t, f"rerun_{k}")
        sentp = os.path.join(d, "input_files.json")
        files = json.load(open(sentp)).get("files", []) if os.path.exists(sentp) else []
        status = nsm["status_of"](d, t)
        rp = os.path.join(d, "test", "test_record.json")
        rec = json.load(open(rp)) if os.path.exists(rp) else None
        passed = bool(rec and rec.get("passed"))
        note = str((rec or {}).get("split_note") or (rec or {}).get("not_run") or "")
        left_out = note.startswith("header missing") or note.startswith("several files sent")
        changed = nsm["source_files"]((rec or {}).get("changed") or [])
        log = nsm["read"](os.path.join(d, "test", "test.log")) + nsm["read"](os.path.join(d, "test", "test_stderr.log"))
        not_applied = bool(nsm["APPLY_FAIL"].search(log)) or bool(nsm["NO_PATCH_PROGRAM"].search(log))
        got_all = "n/a" if fg == "none" else "unknown" if fg == "unknown" else "yes" if set(need) <= set(files) else "no"
        if os.path.exists(os.path.join(d, "no_input.json")) or status == "NO RESULT" or rec is None or (rec.get("not_run") and not left_out):
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
        elif fg in ("one", "two to seven") and len(changed) < len(need):
            cause = "changed fewer source files than the fix"
        elif nsm["last_failure_line"](os.path.join(d, "test")) in nulls:
            cause = "failed like the null patch"
        else:
            cause = "failed otherwise"
        A.append(dict(tag=t, rerun=str(k), files_sent=str(len(files)), fix_group=fg, got_every_fix_file=got_all,
                      left_out_a_file=str(left_out), status=status, test_passed=str(passed), calibration_group=group, cause=cause))
assert len(A) == len(S)
SRCG = "AgentIssue-Bench/case_check/gpt-oss-120b/<tag>/shipped_negative_<k> and the run records, rules of analyze_multifile.py"
gi = collections.defaultdict(set)
for r in A:
    gi[r["calibration_group"]].add(r["tag"])
GROUPS = [("fails without a fix", "fail"), ("passes without a fix", "null"), ("unstable", "mixed")]
for g, k in GROUPS:
    G = [r for r in A if r["calibration_group"] == g]
    add(f"grp_{k}_issues", len(gi[g]), f"issues whose original code gives the group '{g}'", SRCG, "five original-code runs per issue")
    add(f"grp_{k}_runs", len(G), f"repair runs in issues of the group '{g}'", SRCG, "rows per group")
    c = collections.Counter((r["status"], r["test_passed"]) for r in G)
    for (st, pp), v in [(("ACCEPTED", "True"), "ap"), (("ACCEPTED", "False"), "af"), (("FAILED", "True"), "fp"), (("FAILED", "False"), "ff"), (("NO RESULT", "False"), "nr")]:
        add(f"grp_{k}_{v}", c[(st, pp)], f"runs of group '{g}' with status {st} and test passed {pp}", SRCG, "status, test_passed")
assert sum(len(v) for v in gi.values()) == len(tags)
CAUSES = ["no repair", "test passes without a fix", "test unstable", "test passed",
          "did not get every file the fix touches", "left out a file it got", "patch did not apply",
          "changed fewer source files than the fix", "failed like the null patch", "failed otherwise"]
cc = collections.Counter(r["cause"] for r in A)
assert set(cc) <= set(CAUSES) and sum(cc.values()) == len(A)
for i, c in enumerate(CAUSES):
    for s, v in [(None, "runs"), ("ACCEPTED", "acc"), ("FAILED", "fail"), ("NO RESULT", "nores")]:
        n = sum(r["cause"] == c and (s is None or r["status"] == s) for r in A)
        add(f"cause{i}_{v}", n, f"runs with cause '{c}'" + (f", status {s}" if s else ""), SRCG, "cause, status")
sep = [r for r in A if r["calibration_group"] == "fails without a fix"]
for fg in ["one", "two to seven", "unknown", "none"]:
    F = [r for r in sep if r["fix_group"] == fg]
    add(f"fix_{fg.replace(' ', '_')}_issues", len({r['tag'] for r in F}), f"issues that fail without a fix whose fix touches '{fg}' source files", SRCG, "fix_group")
    add(f"fix_{fg.replace(' ', '_')}_runs", len(F), f"runs of those issues", SRCG, "rows")
    add(f"fix_{fg.replace(' ', '_')}_got", sum(r["got_every_fix_file"] == "yes" for r in F), "of those runs, SelfHeal got every fix file", SRCG, "got_every_fix_file yes")
    add(f"fix_{fg.replace(' ', '_')}_passed", sum(r["test_passed"] == "True" for r in F), "of those runs, the shipped test passed", SRCG, "test_passed True")
two = [r for r in A if r["files_sent"].isdigit() and int(r["files_sent"]) >= 2 and r["status"] != "NO RESULT"]   # analyze_multifile.py line 188
lo = [r for r in two if r["left_out_a_file"] == "True"]
add("sent_two_or_more", len(two), "runs with a result sent two or more files", SRCG, "files_sent >= 2")
add("left_out", len(lo), "of those, the final code left out a file it got", SRCG, "left_out_a_file True")
add("left_out_acc", sum(r["status"] == "ACCEPTED" for r in lo), "of those, ACCEPTED", SRCG, "status")
add("left_out_fail", sum(r["status"] == "FAILED" for r in lo), "of those, FAILED", SRCG, "status")
add("sep_failures", sum(r["test_passed"] != "True" for r in sep), "runs of the issues that fail without a fix whose shipped test failed", SRCG, "group fails without a fix, test_passed not True")

# what each repair changed against the source files the developer's fix touches, issues that fail without a fix.
# The source-file rule and the developer patch's files are analyze_multifile.py's own functions.
amf = open(f"{AI}/code/analyze_multifile.py").read()
nsx = {"re": re, "os": os}
exec(amf[amf.index("TEST = re.compile"):amf.index("APPLY_FAIL")], nsx)
exec(amf[amf.index("def source_files"):amf.index("def fix_group")], nsx)
nsx["ISSUES"] = f"{AI}/inputs/issues"
SS = {(r["tag"], r["rerun"]): r for r in S}
CH = collections.Counter()
for r in sep:
    need = set(nsx["fix_files"](r["tag"]))
    rec = f"{AI}/{M}/{r['tag']}/rerun_{r['rerun']}/test/test_record.json"
    ch = set(nsx["source_files"](json.load(open(rec)).get("changed") or [])) if os.path.exists(rec) else None
    if r["fix_group"] == "unknown":
        k = "more_than_seven"
    elif r["fix_group"] == "none":
        k = "no_source_file"
    elif ch is None:
        k = "no_record"
    else:
        k = "every" if need <= ch else "some" if need & ch else "none"
    CH[(k, "runs")] += 1; CH[(k, "passed")] += r["test_passed"] == "True"; CH[(k, "succ")] += SS[(r["tag"], r["rerun"])]["final_success"] == "True"
    CH[(k, "issues", r["tag"])] = 1
src = "AgentIssue-Bench/SelfHeal/inputs/issues/<tag>/developer.patch and <model>/<tag>/rerun_<k>/test/test_record.json changed"
KS = ["every", "some", "none", "more_than_seven", "no_source_file", "no_record"]
for k in KS:
    add(f"chf_{k}_issues", sum(1 for key in CH if key[0] == k and key[1] == "issues"), f"issues that fail without a fix with a run in class '{k}'", src, "source_files and fix_files of analyze_multifile.py")
    add(f"chf_{k}_runs", CH[(k, "runs")], f"runs whose repair changed '{k}' of the source files the developer's fix touches", src, "source_files and fix_files of analyze_multifile.py")
    add(f"chf_{k}_passed", CH[(k, "passed")], "of those runs, shipped test passed", src, "test_passed")
    add(f"chf_{k}_succ", CH[(k, "succ")], "of those runs, successes", src, "final_success")
assert sum(CH[(k, "runs")] for k in KS) == len(sep)

# the critic's first verdict, from SelfHeal's result files
sep_tags = gi["fails without a fix"]
att = []
for r in S:
    f = glob.glob(f"{AI}/{M}/{r['tag']}/rerun_{r['rerun']}/Fix-Agent/results/*_result.txt")
    if not f:
        continue
    t = open(f[0]).read()
    att.append(dict(tag=r["tag"], status=re.search(r"(?m)^Status: (\w+)", t).group(1), final=int(re.search(r"(?m)^Final Attempt: (\d+)", t).group(1)),
                    durs=[float(x) for x in re.findall(r"(?m)^Duration: ([\d.]+) seconds", t)], success=r["final_success"] == "True"))
for lab, sel in [("fail", [a for a in att if a["tag"] in sep_tags]), ("all", att)]:
    acc1 = [a for a in sel if a["status"] == "ACCEPTED" and a["final"] == 1]
    rej1 = [a for a in sel if not (a["status"] == "ACCEPTED" and a["final"] == 1)]
    share = sum(a["durs"][0] for a in sel) / sum(sum(a["durs"]) for a in sel)
    src, how = "AgentIssue-Bench/SelfHeal/gpt-oss-120b/<tag>/rerun_<k>/Fix-Agent/results/<tag>_result.txt", "Status, Final Attempt, Duration lines"
    add(f"v1_{lab}_runs", len(sel), f"runs with a result file, {lab} issues", src, how)
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
# test share of time, runs with both a repair time and a shipped test time
for lab, keep in [("fail", lambda t: t in sep_tags), ("all", lambda t: True)]:
    rep = tst = n = 0
    for r in S:
        if not keep(r["tag"]):
            continue
        d = f"{AI}/{M}/{r['tag']}/rerun_{r['rerun']}"
        if not (os.path.exists(f"{d}/run_record.json") and os.path.exists(f"{d}/test/test_record.json")):
            continue
        rr, tr = json.load(open(f"{d}/run_record.json")), json.load(open(f"{d}/test/test_record.json"))
        if "seconds" not in tr:
            continue
        rep += sum(a["seconds"] for a in rr["attempts"]); tst += tr["seconds"]; n += 1
    src = "AgentIssue-Bench/SelfHeal/gpt-oss-120b/<tag>/rerun_<k>/run_record.json and test/test_record.json"
    add(f"ts_{lab}_runs", n, f"runs with both a repair time and a test time, {lab} issues", src, "both files present, test record has seconds")
    add(f"ts_{lab}_repair_h", r2(rep / 3600), "repair hours", src, "sum of run_record attempts seconds / 3600")
    add(f"ts_{lab}_repair_min_run", r2(rep / 60 / n), "SelfHeal minutes per run", src, "sum of run_record attempts seconds / 60 / runs")
    add(f"ts_{lab}_test_min_run", r2(tst / 60 / n), "test minutes per run", src, "sum of test_record seconds / 60 / runs")
    add(f"ts_{lab}_test_h", r2(tst / 3600), "shipped test hours", src, "sum of test_record seconds / 3600")
    add(f"ts_{lab}_share", r3(tst / (rep + tst)), "test share of repair plus test time", src, "test / (repair + test)")

# web search, three models, fix agent web_search and critic verify_api_usage
TOOLS = {"web_search", "verify_api_usage"}
errtext = collections.Counter()
for m in MODELS:
    logs = glob.glob(f"{AI}/{m}/**/relay_log_run_agent.jsonl", recursive=True)
    calls_all = []
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
    src, how = f"AgentIssue-Bench/SelfHeal/{m}/**/relay_log_run_agent.jsonl", "web_search and verify_api_usage tool replies, kept and moved-aside runs"
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
    f.write("# Number registry, SelfHeal on AgentIssue-Bench with three models\n\n")
    f.write("Rows written by `docs/selfheal_agentissue_gptoss_report_numbers.py`. The report is checked with\n\n")
    f.write("```\npython3 ~/.claude/skills/number-check/scripts/check_numbers.py --registry docs/selfheal_agentissue_gptoss_report_numbers.md "
            "--ignore '^[0-9]\\.[0-9](\\.[0-9])?$' --ignore '^(2611\\.09792|1603\\.09326|2604\\.17699|2505\\.20749)$' docs/selfheal_agentissue_gptoss_report.md\n```\n\n")
    f.write("The ignore patterns skip section numbers and the four arXiv ids.\n\n")
    f.write("| name | value | what it counts | source file | how it is computed | date read |\n|---|---|---|---|---|---|\n")
    for r in rows:
        f.write("| " + " | ".join(r) + f" | {today} |\n")
print(len(rows), "rows written to", OUT)
for r in rows:
    print(r[0], r[1])
