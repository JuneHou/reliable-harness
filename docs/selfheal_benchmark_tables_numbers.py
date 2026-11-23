"""Compute every number of docs/selfheal_benchmark_tables.md and write its registry
docs/selfheal_benchmark_tables_numbers.md (the number-check skill, section 0). Reads only.

Sources
- SelfHeal paper (arXiv 2604.17699 v1), Table 2, parsed from the saved arXiv HTML page.
- SelfHeal repository, Detailed Result.xlsx, the per-case sheets of SelfHeal with its three models.
- AgentIssue-Bench paper (arXiv 2505.20749), Table 6, parsed from the saved arXiv HTML page.
- Our records: AgentDefect/SelfHeal/test_scores.csv and result files, AgentIssue-Bench/SelfHeal/test_scores.csv.

  python docs/selfheal_benchmark_tables_numbers.py
"""
import csv
import datetime
import glob
import html
import json
import re
import statistics

import openpyxl

H = "/data/wang/junh/githubs/stochastic-harness"
PAPERS = "/tmp/claude-29714/-data-wang-junh-githubs-stochastic-harness/ce7a513c-8c48-441f-88c9-272c3d56b0e8/scratchpad/papers_html"
SH = "/data/wang/junh/githubs/SelfHeal"
OUT = f"{H}/docs/selfheal_benchmark_tables_numbers.md"
MODELS = ["gpt-oss-120b", "DeepSeek-V4.1-Flash", "GLM-5.3"]
today = datetime.date.today().isoformat()
rows = []


def add(name, value, what, source, how):
    rows.append((name, str(value), what, source, how))


def text_of(path):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", open(path, encoding="utf-8").read())))


def two_sigma(xs):
    return 2 * statistics.stdev(xs) if len(xs) > 1 else 0.0


# 1. SelfHeal paper Table 2, as published
raw = open(f"{PAPERS}/SelfHeal.html", encoding="utf-8").read()
cap = raw.find("Performance comparison of bug identification and repair")
tab = raw[raw.rfind("<figure", 0, cap):raw.find("</figure>", cap)]
prev = None
for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tab, re.S):
    cells = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
    if not cells or cells[0] == "App.":
        continue
    app = cells[0] or prev
    prev = app
    key = f"{app}_{cells[1]}".replace(" ", "").replace(".", "").replace("-", "")
    for col, v in zip(["repair", "line", "fn", "comp", "attempts"], cells[2:7]):
        add(f"sh_t2_{key}_{col}", v, f"SelfHeal paper Table 2, {app} with {cells[1]}, column {col}", "SelfHeal paper arXiv 2604.17699 v1, Table 2", "copied")
add("sh_cases", 37, "AgentDefect cases in the SelfHeal paper's evaluation", "SelfHeal paper §4.3.1", "'correctly fixing 22 out of 37'")

# 2. the authors' per-case sheet, SelfHeal with three models, on 37 and on our 36 scored cases
wb = openpyxl.load_workbook(f"{SH}/Detailed Result.xlsx", read_only=True)
ours36 = sorted({r["case"] for r in csv.DictReader(open(f"{H}/AgentDefect/SelfHeal/test_scores.csv")) if r["in_table"] == "True"})
assert len(ours36) == 36
for sheet, lab in [("results-agent-gpt", "g52"), ("results-agent-gemini", "g3p"), ("results-agent-claude", "cs4")]:
    recs = [r for r in wb[sheet].iter_rows(min_row=3, values_only=True) if r and r[0] is not None]
    by = {str(int(r[0])) if isinstance(r[0], float) else str(r[0]): r for r in recs}
    assert len(by) == 37, (sheet, len(by))
    for scope, ids in [("37", list(by)), ("36", ours36)]:
        sel = [by[i] for i in ids]
        add(f"sheet_{lab}_{scope}_resolved", sum(int(r[4]) for r in sel), f"cases marked Resolved, {sheet}, {scope} cases", f"{SH}/Detailed Result.xlsx, sheet {sheet}", "sum of the Resolved column")
        add(f"sheet_{lab}_{scope}_rate", f"{sum(int(r[4]) for r in sel) / len(sel):.4f}", f"share of cases marked Resolved, {scope} cases", f"{SH}/Detailed Result.xlsx, sheet {sheet}", "Resolved sum / cases")
        for ci, col in [(1, "line"), (2, "function"), (3, "component")]:
            add(f"sheet_{lab}_{scope}_{col}", f"{sum(int(r[ci]) for r in sel) / len(sel):.4f}", f"share of cases localized at {col} level, {scope} cases", f"{SH}/Detailed Result.xlsx, sheet {sheet}", f"{col} sum / cases")
        add(f"sheet_{lab}_{scope}_attempts", f"{statistics.mean(r[5] for r in sel):.2f}", f"mean attempts per case, {scope} cases", f"{SH}/Detailed Result.xlsx, sheet {sheet}", "mean of the Attempts column")
        add(f"sheet_{lab}_{scope}_seconds", f"{statistics.mean(r[6] for r in sel):.1f}", f"mean time per case in seconds, {scope} cases", f"{SH}/Detailed Result.xlsx, sheet {sheet}", "mean of the Time column")

# 3. our AgentDefect runs, three models, the 36 scored cases, five runs
T = [r for r in csv.DictReader(open(f"{H}/AgentDefect/SelfHeal/test_scores.csv")) if r["in_table"] == "True"]
for m in MODELS:
    k = m.split("-")[0].lower()
    M = [r for r in T if r["model"] == m]
    assert len(M) == 180, (m, len(M))
    succ = [sum(r["final_success"] == "True" for r in M if r["rerun"] == str(j)) / 36 for j in range(1, 6)]
    tp = [sum(r["final_test_passed"] == "True" for r in M if r["rerun"] == str(j)) / 36 for j in range(1, 6)]
    acc = sum(r["final_status"] == "ACCEPTED" for r in M)
    src = "AgentDefect/SelfHeal/test_scores.csv"
    add(f"ad_{k}_succ_mean", f"{statistics.mean(succ):.4f}", f"{m}, share of the 36 cases where the critic accepted and the test passed, mean over five runs", src, "per run share, mean")
    add(f"ad_{k}_succ_2s", f"{two_sigma(succ):.4f}", f"{m}, two standard deviations of that share over the five runs", src, "2 x sample sd over runs")
    add(f"ad_{k}_test_mean", f"{statistics.mean(tp):.4f}", f"{m}, share of the 36 cases whose returned code passed the test, mean over five runs", src, "per run share, mean")
    add(f"ad_{k}_test_2s", f"{two_sigma(tp):.4f}", f"{m}, two standard deviations of that share over the five runs", src, "2 x sample sd over runs")
    add(f"ad_{k}_accepted", acc, f"{m}, runs the critic accepted, of 180", src, "final_status ACCEPTED")
    att, secs = [], []
    for r in M:
        f = glob.glob(f"{H}/AgentDefect/SelfHeal/{m}/{r['case']}/rerun_{r['rerun']}/Fix-Agent/results/*_result.txt")
        if f:
            t = open(f[0]).read()
            att.append(int(re.search(r"(?m)^Final Attempt: (\d+)", t).group(1)))
        rr = f"{H}/AgentDefect/SelfHeal/{m}/{r['case']}/rerun_{r['rerun']}/run_record.json"
        try:
            secs.append(sum(a["seconds"] for a in json.load(open(rr))["attempts"]))
        except (OSError, KeyError, ValueError):
            pass
    add(f"ad_{k}_attempts", f"{statistics.mean(att):.2f}", f"{m}, mean attempts per run", f"AgentDefect/SelfHeal/{m}/<case>/rerun_<k>/Fix-Agent/results", "mean of Final Attempt")
    add(f"ad_{k}_attempt_runs", len(att), f"{m}, runs with a result file", f"AgentDefect/SelfHeal/{m}/<case>/rerun_<k>/Fix-Agent/results", "count")
    add(f"ad_{k}_seconds", f"{statistics.mean(secs):.1f}", f"{m}, mean SelfHeal time per run in seconds", f"AgentDefect/SelfHeal/{m}/<case>/rerun_<k>/run_record.json", "mean of summed attempt seconds")
    add(f"ad_{k}_seconds_runs", len(secs), f"{m}, runs with a time record", f"AgentDefect/SelfHeal/{m}/<case>/rerun_<k>/run_record.json", "count")
# the same three models on all 37 cases, the denominator of the SelfHeal paper's Table 2
TA = list(csv.DictReader(open(f"{H}/AgentDefect/SelfHeal/test_scores.csv")))
for m in MODELS:
    k = m.split("-")[0].lower()
    M = [r for r in TA if r["model"] == m]
    assert len(M) == 185, (m, len(M))
    succ = [sum(r["final_success"] == "True" for r in M if r["rerun"] == str(j)) / 37 for j in range(1, 6)]
    add(f"ad37_{k}_succ_mean", f"{statistics.mean(succ):.4f}", f"{m}, share of the 37 cases where the critic accepted and the test passed, mean over five runs", "AgentDefect/SelfHeal/test_scores.csv", "per run share of 37, mean")
    add(f"ad37_{k}_succ_2s", f"{two_sigma(succ):.4f}", f"{m}, two standard deviations of that share over five runs", "AgentDefect/SelfHeal/test_scores.csv", "2 x sample sd")
    att = []
    for r in M:
        f = glob.glob(f"{H}/AgentDefect/SelfHeal/{m}/{r['case']}/rerun_{r['rerun']}/Fix-Agent/results/*_result.txt")
        if f:
            att.append(int(re.search(r"(?m)^Final Attempt: (\d+)", open(f[0]).read()).group(1)))
    add(f"ad37_{k}_attempts", f"{statistics.mean(att):.2f}", f"{m}, mean attempts per run over the 37 cases", f"AgentDefect/SelfHeal/{m}/<case>/rerun_<k>/Fix-Agent/results", "mean of Final Attempt")
    add(f"ad37_{k}_attempt_runs", len(att), f"{m}, runs with a result file over the 37 cases", f"AgentDefect/SelfHeal/{m}/<case>/rerun_<k>/Fix-Agent/results", "count")
add("ad37_runs_per_model", 185, "runs per model over the 37 cases, five per case", "AgentDefect/SelfHeal/test_scores.csv", "rows per model")
add("ad_runs_per_model", 180, "scored runs per model, five per case", "AgentDefect/SelfHeal/test_scores.csv", "in_table rows per model")
add("ad_cases", 36, "AgentDefect cases in our score tables", "AgentDefect/SelfHeal/test_scores.csv", "distinct in_table case")
add("ad_dropped_case", "79776520", "case left out of our score tables", "AgentDefect/SelfHeal/test_scores.csv", "in_table False")

# 4. AgentIssue-Bench paper Table 6, as published (mean over three runs with two sigma)
t = text_of(f"{PAPERS}/AgentIssueBench.html").replace("\\pm{}", "")
i = t.find("Table 6 : Mean results")
seg = t[i:t.find("Appendix E", i)]
num = r"(\d+\.\d+) \( ± [\d.]+ ([\d.]+) \)"
agents = re.findall(r"(Agentless|AutoCodeRover|SWE-agent)?\s*(GPT-4o|Claude-3\.5-S) " + " ".join([num] * 4), seg)
assert len(agents) == 6, len(agents)
cur = None
for a in agents:
    cur = a[0] or cur
    key = f"{cur}_{a[1]}".replace("-", "").replace(".", "")
    for j, col in enumerate(["plausible", "correct", "loc_file", "loc_fn"]):
        add(f"ai_t6_{key}_{col}", a[2 + 2 * j], f"AgentIssue-Bench paper Table 6, {cur} with {a[1]}, {col} mean over three runs", "AgentIssue-Bench paper arXiv 2505.20749, Table 6", "copied")
        add(f"ai_t6_{key}_{col}_2s", a[3 + 2 * j], f"same, two sigma", "AgentIssue-Bench paper arXiv 2505.20749, Table 6", "copied")
i2 = t.find("Table 2 : Overall results of SE agents on AgentIssue-Bench")
seg2 = t[i2:t.find("Quantitative Results", i2)]
rows2 = re.findall(r"(Agentless|AutoCodeRover|SWE-agent)?\s*(GPT-4o|Claude-3\.5-S) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)", seg2)
assert len(rows2) == 6, len(rows2)
cur = None
for a2 in rows2:
    cur = a2[0] or cur
    key = f"{cur}_{a2[1]}".replace("-", "").replace(".", "")
    add(f"ai_t2_{key}_cost", a2[6], f"AgentIssue-Bench paper Table 2, {cur} with {a2[1]}, average cost in dollars", "AgentIssue-Bench paper arXiv 2505.20749, Table 2", "copied")
add("ai_issues", 50, "AgentIssue-Bench issues", "AgentIssue-Bench paper", "'50 agent issues'")

# 5. SelfHeal with gpt-oss-120b on AgentIssue-Bench, the paper's plausible metric through the shipped scoring path
S = [r for r in csv.DictReader(open(f"{H}/AgentIssue-Bench/SelfHeal/test_scores.csv")) if r["model"] == "gpt-oss-120b" and r["evaluator"] == "shipped"]
assert len(S) == 250
per = [100 * sum(r["final_test_passed"] == "True" for r in S if r["rerun"] == str(j)) / 50 for j in range(1, 6)]
src = "AgentIssue-Bench/SelfHeal/test_scores.csv, shipped rows"
add("ai_sh_plaus_5", f"{statistics.mean(per):.2f}", "SelfHeal gpt-oss-120b, percent of the 50 issues whose returned code passes the shipped test, mean over five runs", src, "per run percent, mean")
add("ai_sh_plaus_5_2s", f"{two_sigma(per):.2f}", "same, two sigma over five runs", src, "2 x sample sd")
add("ai_sh_plaus_3", f"{statistics.mean(per[:3]):.2f}", "same, mean over runs 1 to 3", src, "per run percent, mean")
add("ai_sh_plaus_3_2s", f"{two_sigma(per[:3]):.2f}", "same, two sigma over runs 1 to 3", src, "2 x sample sd")
for j, v in enumerate(per, 1):
    add(f"ai_sh_plaus_run{j}", f"{v:.0f}", f"percent of issues passing in run {j}", src, "count / 50 x 100")
passes = sum(r["final_test_passed"] == "True" for r in S)
add("ai_sh_passing_runs", passes, "runs whose returned code passed the shipped test, of 250", src, "final_test_passed")
add("ai_sh_runs", 250, "SelfHeal runs on AgentIssue-Bench with gpt-oss-120b", src, "rows")
neg = {}
for tg in {r["tag"] for r in S}:
    ps = [json.load(open(p))["passed"] for p in glob.glob(f"{H}/AgentIssue-Bench/case_check/gpt-oss-120b/{tg}/shipped_negative_*/test_record.json")]
    neg[tg] = len(ps) == 5 and all(ps)
add("ai_sh_passing_in_null_issues", sum(r["final_test_passed"] == "True" and neg[r["tag"]] for r in S), "of the passing runs, those in issues whose original code passes the test in all five runs", src, "with case_check shipped_negative records")
add("ai_null_issues", sum(neg.values()), "issues whose original code passes the shipped test in all five runs", "AgentIssue-Bench/case_check/gpt-oss-120b/<tag>/shipped_negative_<k>", "all five passed")
add("ai_sh_success", sum(r["final_success"] == "True" for r in S), "runs the critic accepted and whose code passed, of 250", src, "final_success")

with open(OUT, "w") as f:
    f.write("# Number registry, SelfHeal against the published benchmarks\n\n")
    f.write("Rows written by `docs/selfheal_benchmark_tables_numbers.py`. Checked with\n\n```\npython3 ~/.claude/skills/number-check/scripts/check_numbers.py "
            "--registry docs/selfheal_benchmark_tables_numbers.md --ignore '^[0-9]\\.[0-9](\\.[0-9])?$' --ignore '^(2604\\.17699|2505\\.20749)$' docs/selfheal_benchmark_tables.md\n```\n\n")
    f.write("| name | value | what it counts | source file | how it is computed | date read |\n|---|---|---|---|---|---|\n")
    for r in rows:
        f.write("| " + " | ".join(r) + f" | {today} |\n")
print(len(rows), "rows")
for r in rows:
    print(r[0], r[1])
