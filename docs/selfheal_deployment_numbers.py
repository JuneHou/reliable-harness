"""Compute every number of docs/selfheal_deployment.md from its source files and write the registry
docs/selfheal_deployment_numbers.md (the number-check skill, section 0).

  python docs/selfheal_deployment_numbers.py
"""
import collections
import csv
import datetime
import glob
import json
import os
import re
import sys
import zipfile

H = "/data/wang/junh/githubs/stochastic-harness"
AD = f"{H}/AgentDefect/SelfHeal"
AI = f"{H}/AgentIssue-Bench/SelfHeal"
ZIP = "/data/wang/junh/githubs/SelfHeal/AgentDefect.zip"
MODELS = ["gpt-oss-120b", "GLM-5.3", "DeepSeek-V4.1-Flash"]
csv.field_size_limit(10**9)
sys.path.insert(0, f"{AD}/code")
from test_repairs import LISTS, requirements  # noqa: E402

rows = []
today = datetime.date.today().isoformat()


def add(name, value, what, source, how):
    rows.append((name, str(value), what, source, how))


def status_counts(m):
    c = collections.Counter()
    for f in glob.glob(f"{AD}/{m}/[0-9h]*/rerun_*/Fix-Agent/results/*_result.txt"):
        c[re.search(r"(?m)^Status:\s*(\S+)", open(f).read()).group(1)] += 1
    return c


# AgentDefect inputs
z = zipfile.ZipFile(ZIP)
cases = sorted({p.split("/")[1] for p in z.namelist() if p.count("/") >= 2 and not p.startswith("__MACOSX") and p.split("/")[1]})
add("ad_cases", len(cases), "AgentDefect case folders", "/data/wang/junh/githubs/SelfHeal/AgentDefect.zip", "distinct second path parts")
add("ad_so_cases", sum(c != "hf-26" for c in cases), "AgentDefect cases from Stack Overflow", "/data/wang/junh/githubs/SelfHeal/AgentDefect.zip", "case folders other than hf-26")
fp = list(csv.DictReader(open(f"{AD}/inputs/fix-pattern.csv", encoding="utf-8")))
add("fp_rows", len(fp), "rows of fix-pattern.csv, the StackOverflow sheet of Fix Patterns.xlsx", "AgentDefect/SelfHeal/inputs/fix-pattern.csv", "row count")
add("fp_posts", len({r["id"] for r in fp}), "distinct posts in fix-pattern.csv", "AgentDefect/SelfHeal/inputs/fix-pattern.csv", "distinct id")
add("fp_patterns", len({r["Fix Pattern"] for r in fp}), "distinct Fix Pattern names in fix-pattern.csv", "AgentDefect/SelfHeal/inputs/fix-pattern.csv", "distinct Fix Pattern")
tr = list(csv.DictReader(open(f"{AD}/inputs/train_descriptions.csv", encoding="utf-8")))
add("train_posts", len(tr), "training posts the Stack Exchange API returned", "AgentDefect/SelfHeal/inputs/train_descriptions.csv", "row count")
sm = {m: len({r["id"] for r in csv.DictReader(open(f"{AD}/{m}/rules/id_summaries2.csv", encoding="utf-8"))}) for m in MODELS}
assert len(set(sm.values())) == 1
add("ad_summaries", sm[MODELS[0]], "post summaries per model in the AgentDefect rules step, the same for all three models", "AgentDefect/SelfHeal/gpt-oss-120b/rules/id_summaries2.csv", "distinct id, each model")
add("ad_excluded_posts", len({r["id"] for r in fp}) - sm[MODELS[0]], "training posts left out because they are AgentDefect cases", "AgentDefect/SelfHeal/inputs/fix-pattern.csv", "posts minus summaries")
rr = {m: len(list(csv.DictReader(open(f"{AD}/{m}/rules/fix_pattern_rules.csv", encoding="utf-8")))) for m in MODELS}
assert len(set(rr.values())) == 1
add("ad_rules", rr[MODELS[0]], "fix rules per model", "AgentDefect/SelfHeal/gpt-oss-120b/rules/fix_pattern_rules.csv", "row count, each model")
# AgentDefect reruns
sc = {m: status_counts(m) for m in MODELS}
add("ad_reruns_per_model", sum(sc[MODELS[0]].values()), "kept SelfHeal reruns per model on AgentDefect, 37 cases times five", "AgentDefect/SelfHeal/<model>/<case>/rerun_<k>/Fix-Agent/results", "result files per model")
add("ad_reruns_total", sum(sum(c.values()) for c in sc.values()), "kept SelfHeal reruns on AgentDefect, three models", "AgentDefect/SelfHeal/<model>/<case>/rerun_<k>/Fix-Agent/results", "result files")
add("ad_gptoss_accepted", sc["gpt-oss-120b"]["ACCEPTED"], "gpt-oss-120b reruns SelfHeal marked ACCEPTED", "AgentDefect/SelfHeal/gpt-oss-120b", "Status line of result files")
add("ad_gptoss_failed", sc["gpt-oss-120b"]["FAILED"], "gpt-oss-120b reruns SelfHeal marked FAILED", "AgentDefect/SelfHeal/gpt-oss-120b", "Status line of result files")
for m, key in [("gpt-oss-120b", "gptoss"), ("GLM-5.3", "glm"), ("DeepSeek-V4.1-Flash", "ds")]:
    for d in ["_search_failed", "_stopped", "_outage", "_not_streamed", "_not_streamed/_search_failed", "_not_streamed/_token_limit"]:
        n = len(glob.glob(f"{AD}/{m}/{d}/[0-9h]*/rerun_*"))
        if n:
            add(f"ad_{key}{d.replace('/', '')}", n, f"{m} reruns in {d}", f"AgentDefect/SelfHeal/{m}/{d}", "rerun folders")
cut = 0
for d in glob.glob(f"{AD}/GLM-5.3/_not_streamed/_token_limit/*/rerun_*"):
    hit = any(ch.get("finish_reason") == "length" for l in open(d + "/relay_log_run_agent.jsonl")
              for ch in ((json.loads(l).get("response") or {}).get("choices") or []))
    cut += hit
add("ad_glm_tl_cut", cut, "GLM-5.3 reruns of the first attempt before streaming with at least one reply ended for length", "AgentDefect/SelfHeal/GLM-5.3/_not_streamed/_token_limit/*/rerun_*/relay_log_run_agent.jsonl", "finish_reason length")
glm_calls = sum(1 for _ in open(f"{AD}/GLM-5.3/_not_streamed/rules/relay_log_extract_summary.jsonl"))
add("ad_glm_summary_calls_ns", glm_calls, "GLM-5.3 summary calls in the rules step before the streaming redo, one repeated after a reply ended for length", "AgentDefect/SelfHeal/GLM-5.3/_not_streamed/rules/relay_log_extract_summary.jsonl", "line count")
add("ad_glm_summary_calls", sum(1 for _ in open(f"{AD}/GLM-5.3/rules/relay_log_extract_summary.jsonl")), "GLM-5.3 summary calls in the kept streamed rules step", "AgentDefect/SelfHeal/GLM-5.3/rules/relay_log_extract_summary.jsonl", "line count")
# Fix plan departure 16: calibration, audits, the streaming check
sys.path.insert(0, f"{AD}/code")
import test_repairs as _tr  # noqa: E402
add("ad_calib_first", len(_tr.CALIB_FIRST), "AgentDefect cases calibrated first, departures 3 and 10", "AgentDefect/SelfHeal/code/test_repairs.py", "CALIB_FIRST")
add("ad_calib_changed", len(_tr.CALIB_FIRST) - 2, "AgentDefect cases whose environment, fixture or test was changed, departure 3", "AgentDefect/SelfHeal/code/test_repairs.py", "CALIB_FIRST without the two Ollama cases 79149108 and 79638234")
add("ad_calib_rest", len(set(_tr.case_ids()) - _tr.CALIB_LEFT_OUT - set(_tr.CALIB_FIRST)), "AgentDefect cases in the score tables calibrated after the plan audit", "AgentDefect/SelfHeal/code/test_repairs.py", "case_ids minus CALIB_LEFT_OUT minus CALIB_FIRST")
amr = list(csv.DictReader(open(f"{AD}/audit_models_read.csv")))
add("ad_audit_model_replaced", len(amr), "tested repairs whose own chat model the relay served with the rerun's ARC model", "AgentDefect/SelfHeal/audit_models_read.csv", "row count")
add("ad_audit_model_replaced_pass", sum(r["test_passed"] == "True" for r in amr), "of those, repairs whose test passed", "AgentDefect/SelfHeal/audit_models_read.csv", "test_passed True")
asr = list(csv.DictReader(open(f"{AD}/audit_search_read.csv")))
add("audit_search_distinct", len(asr), "distinct flagged search results, both datasets, read by hand", "AgentDefect/SelfHeal/audit_search_read.csv", "row count")
add("audit_search_ai_hits", sum(int(r["hits"]) for r in asr if r["dataset"] == "AgentIssue-Bench"), "flagged search results in AgentIssue-Bench reruns", "AgentDefect/SelfHeal/audit_search_read.csv", "sum of hits")
add("arc_bad_gateway", 502, "HTTP status of the one GLM-5.3 call without streamed pieces, 77385587 rerun 2 line 2", "AgentDefect/SelfHeal/GLM-5.3/77385587/rerun_2/relay_log_run_agent.jsonl", "status field")
add("arc_method_not_allowed", 405, "HTTP status ARC returns for the legacy /v1/completions endpoint", "AgentDefect/SelfHeal/*/76897509/rerun_*/test/relay_log_test.jsonl", "status field of /v1/completions calls")
add("arc_cap", 8000, "token cap ARC sets on replies that are not streamed", "AgentDefect/SelfHeal/code/relay.py", "module docstring")
# AgentDefect tests
add("ad_lists", len(LISTS), "different requirement lists of the 37 cases", "AgentDefect/SelfHeal/code/test_repairs.py", "LISTS")
pins = set()
for n in LISTS:
    pins |= set(requirements(LISTS[n][0])[1])
add("ad_pins", len(pins), "different pins over the requirement lists", "AgentDefect/SelfHeal/code/test_repairs.py", "union of requirements over LISTS")
recs = {json.load(open(f))["env"]: json.load(open(f)) for f in glob.glob(f"{AD}/test_env_logs/list_*_install.json")}
add("ad_envs", len(recs), "test environments, the 15 lists plus list_1b and list_1c", "AgentDefect/SelfHeal/test_env_logs/list_*_install.json", "install records")
add("ad_added_typical", collections.Counter(len(r["added"]) for r in recs.values()).most_common(1)[0][0], "packages pip check added in 15 of the 17 environments", "AgentDefect/SelfHeal/test_env_logs/list_*_install.json", "most common len(added)")
add("ad_envs_with_typical_added", sum(len(r["added"]) == 17 for r in recs.values()), "environments where pip check added 17 packages", "AgentDefect/SelfHeal/test_env_logs/list_*_install.json", "count of len(added) == 17")
add("ad_added_list13", len(recs["13"]["added"]), "packages pip check added for list 13", "AgentDefect/SelfHeal/test_env_logs/list_13_install.json", "len(added)")
add("ad_list1c_replaced", len(recs["1c"]["pins_replaced"]), "pins of list_1c at list 4's versions", "AgentDefect/SelfHeal/test_env_logs/list_1c_install.json", "len(pins_replaced)")
tests = len(glob.glob(f"{AD}/*/[0-9h]*/rerun_*/test/test_record.json"))
add("ad_tests", tests, "test records of the AgentDefect repairs, one per rerun", "AgentDefect/SelfHeal/<model>/<case>/rerun_<k>/test/test_record.json", "file count")
add("ad_tests_per_case", 15, "tests per case, three models times five reruns", "AgentDefect/SelfHeal/code/test_repairs.py", "MODELS and RERUNS")
logs = {}
for f in ["test_repairs_first.log", "test_repairs_run_1.log", "test_repairs_run_3.log", "test_repairs_run_4.log",
          "test_repairs_run.log", "test_repairs_run_fixes.log", "test_repairs_run_1c.log", "test_repairs_run_1c2.log"]:
    logs[f] = sum(1 for l in open(f"{AD}/{f}") if re.search(r"(passed|failed exit)", l))
    add(f"ad_log_{f[:-4]}", logs[f], f"tests run in {f}", f"AgentDefect/SelfHeal/{f}", "lines with passed or failed exit")
add("ad_test_runs_total", sum(logs.values()), "test runs over all AgentDefect test logs, deleted ones included", "AgentDefect/SelfHeal/test_repairs_*.log", "sum of the log rows above")
sub = sorted({p.split("/")[1] for p in z.namelist() if not p.startswith("__MACOSX") and p.count("/") >= 3 and p.split("/")[-1] and not p.split("/")[-1].startswith("._")})
folders = 0
for c in sub:
    files = [os.path.join(*p.split("/")[2:]) for p in z.namelist() if not p.startswith("__MACOSX") and p.split("/")[1] == c and p.count("/") >= 3 and p.split("/")[-1] and not p.split("/")[-1].startswith("._")]
    folders += sum(all(os.path.exists(os.path.join(t, f)) for f in files) for t in glob.glob(f"{AD}/*/{c}/rerun_*/test"))
add("ad_subfolder_test_folders", folders, "final test folders of the six cases with subfolder files that hold every such file", "/data/wang/junh/githubs/SelfHeal/AgentDefect.zip", "case files in subfolders checked in each */<case>/rerun_*/test")
add("ad_table_cases", len(cases) - 1, "cases in the AgentDefect success table, 79776520 left out", "AgentDefect/SelfHeal/code/score_tests.py", "cases minus DROPPED")
add("ad_table_reruns", (len(cases) - 1) * 5, "reruns per model in the AgentDefect success table", "AgentDefect/SelfHeal/code/score_tests.py", "36 cases times five")
add("pg_port", 5432, "Postgres port the 79497660 test connects to", "AgentDefect/SelfHeal/code/test_repairs.py", "start_postgres")
add("ad_ollama_port", 11434, "port of the local Ollama server", "AgentDefect/SelfHeal/code/test_repairs.py", "OLLAMA_URL")
# AgentIssue-Bench
ent = json.load(open("/data/wang/junh/githubs/AgentIssue-Bench/motivation_experiment/artifacts/agentissue/entrypoints.json"))
add("aib_issues", len(ent), "AgentIssue-Bench issues", "AgentIssue-Bench/motivation_experiment/artifacts/agentissue/entrypoints.json", "records")
add("aib_amd64", sum(e["architecture"] == "amd64" for e in ent), "issues whose published image is built for amd64", "AgentIssue-Bench/motivation_experiment/artifacts/agentissue/entrypoints.json", "architecture amd64")
add("aib_rebuilt", len([d for d in os.listdir(f"{H}/AgentIssue-Bench/images_amd64") if os.path.isdir(f"{H}/AgentIssue-Bench/images_amd64/{d}")]), "issues rebuilt for amd64", "AgentIssue-Bench/images_amd64", "tag folders")
ir = [json.load(open(f)) for f in glob.glob(f"{AI}/inputs/issues/*/record.json")]
add("aib_tree_image", sum(r["tree_source"].startswith("image") for r in ir), "issues whose repository files come from the image", "AgentIssue-Bench/SelfHeal/inputs/issues/*/record.json", "tree_source")
add("aib_tree_clone", sum(r["tree_source"].startswith("git clone") for r in ir), "issues whose repository files are cloned at the image's buggy commit", "AgentIssue-Bench/SelfHeal/inputs/issues/*/record.json", "tree_source")
named = json.load(open(f"{AI}/inputs/named_files.json"))
add("aib_named", sum(bool(v) for v in named.values()), "issues whose report names at least one repository file", "AgentIssue-Bench/SelfHeal/inputs/named_files.json", "non-empty lists")
add("aib_pick", sum(not v for v in named.values()), "issues whose files the model picks", "AgentIssue-Bench/SelfHeal/inputs/named_files.json", "empty lists")
add("aib_named_max_chars", max(sum(os.path.getsize(f"{AI}/inputs/issues/{t}/repo/{f}") for f in v) for t, v in named.items() if v), "largest joined size of named files of one issue, in bytes (autogen_3361)", "AgentIssue-Bench/SelfHeal/inputs/issues", "sum of file sizes")
add("aib_reruns_per_model", len(ent) * 5, "planned SelfHeal reruns per model on AgentIssue-Bench", "AgentIssue-Bench/SelfHeal/code/driver.py", "50 issues times five")
add("aib_reruns_total", len(ent) * 15, "planned reruns and tests on AgentIssue-Bench, three models", "AgentIssue-Bench/SelfHeal/code/test_repairs.py", "50 issues times 15")
add("aib_timeout", 300, "seconds the benchmark allows one test", "/data/wang/junh/githubs/AgentIssue-Bench/eval_patches.py", "timeout=300, line 112")
pins_sh = [l for l in open(f"{AI}/inputs/env_selfheal_pins.txt") if l.strip()]
add("env_selfheal_pins", len(pins_sh), "distributions installed in the rebuilt selfheal environment", "AgentIssue-Bench/SelfHeal/inputs/env_selfheal_pins.txt", "line count")
pins_028 = [l for l in open(f"{AI}/inputs/env_selfheal_openai028_pins.txt") if l.strip()]
add("env_openai028_pins", len(pins_028), "distributions in the rebuilt selfheal-openai028 environment", "AgentIssue-Bench/SelfHeal/inputs/env_selfheal_openai028_pins.txt", "line count")
picks = glob.glob(f"{AI}/gpt-oss-120b/*/pick/pick.json")
add("http_not_found", 404, "HTTP status GitHub returns for crewAIInc/crewAI issue 1824, page and API", "AgentIssue-Bench/motivation_experiment/artifacts/agentissue/issues/crewai_1824.json", "status note, checked again with curl")
add("check_call_limit", 32768, "length limit I set on an ARC check call, the mistake behind the no length limit rule", "/home/grads/junh/.claude/CLAUDE.md", "section No token limit on any model call, Why")
add("aib_gptoss_picks", len(picks), "issues with a finished gpt-oss-120b file pick", "AgentIssue-Bench/SelfHeal/gpt-oss-120b/*/pick/pick.json", "file count")

# AgentIssue-Bench, fix plan departures 4, 5, 13 and 6
corr = json.load(open(f"{AI}/evaluator/corrections.json"))
add("aib_corrected", len(corr), "issues with a corrected evaluator, departures 5 and 13", "AgentIssue-Bench/SelfHeal/evaluator/corrections.json", "keys")
add("aib_shipped_only", len(ent) - len(corr), "issues with only the shipped evaluator", "AgentIssue-Bench/SelfHeal/evaluator/corrections.json", "50 minus the keys")
CHK = f"{H}/AgentIssue-Bench/case_check/gpt-oss-120b"
groups = collections.Counter()
for ev in ("shipped", "corrected"):
    for t in sorted(os.listdir(CHK)):
        if t.startswith("_"):
            continue
        def _c(k):
            rs = [json.load(open(p))["passed"] for p in glob.glob(f"{CHK}/{t}/{ev}_{k}_*/test_record.json")]
            return (sum(rs), len(rs)) if rs else None
        n, p = _c("negative"), _c("positive")
        if n is None:
            continue
        g = ("separates" if n[0] == 0 and p[0] == p[1] else "both fail" if n[0] == 0 and p[0] == 0
             else "both pass" if n[0] == n[1] and p[0] == p[1] else "mixed")
        groups[(ev, g, t in corr)] += 1
add("aib_cal_corr_separates", groups[("corrected", "separates", True)], "issues whose corrected evaluator passes the developer patch five of five and the null patch none, gpt-oss-120b", "AgentIssue-Bench/case_check/gpt-oss-120b", "five runs of each control")
add("aib_cal_ship_corr_bothfail", groups[("shipped", "both fail", True)], "issues with a corrected evaluator whose shipped evaluator fails both controls five of five, gpt-oss-120b", "AgentIssue-Bench/case_check/gpt-oss-120b", "five runs of each control")
add("aib_cal_ship_bothfail_all", sum(v for (e, g, _), v in groups.items() if e == "shipped" and g == "both fail"), "issues whose shipped evaluator fails both controls, gpt-oss-120b", "AgentIssue-Bench/case_check/gpt-oss-120b", "five runs of each control")
add("aib_cal_separating_final", groups[("corrected", "separates", True)] + groups[("shipped", "separates", False)], "issues whose final evaluator tells the developer patch from the null patch, gpt-oss-120b", "AgentIssue-Bench/case_check/gpt-oss-120b", "corrected evaluator where one exists, else shipped")
aist = collections.Counter()
for d in glob.glob(f"{AI}/gpt-oss-120b/*/rerun_*"):
    t = d.split("/")[-2]
    res = f"{d}/Fix-Agent/results/{t}_result.txt"
    aist[re.search(r"(?m)^Status:\s*(\S+)", open(res, encoding="utf-8").read()).group(1) if os.path.exists(res) else "none"] += 1
add("aib_gptoss_accepted", aist["ACCEPTED"], "gpt-oss-120b AgentIssue-Bench kept reruns SelfHeal marked ACCEPTED", "AgentIssue-Bench/SelfHeal/gpt-oss-120b/<tag>/rerun_<k>/Fix-Agent/results", "Status line")
add("aib_initial_adaptation", len([d for d in glob.glob(f"{AI}/gpt-oss-120b/_initial_adaptation/*/rerun_*") if "/_stopped_by_hand/" not in d]), "gpt-oss-120b reruns of the first adaptation, kept apart", "AgentIssue-Bench/SelfHeal/gpt-oss-120b/_initial_adaptation", "rerun folders")
_or = 0
for p in glob.glob(f"{AI}/DeepSeek-V4.1-Flash/*/rerun_*/run_record.json"):
    _or += json.load(open(p)).get("attempts", [{}])[-1].get("provider") == "openrouter"
add("aib_ds_openrouter", _or, "DeepSeek-V4.1-Flash AgentIssue-Bench kept reruns run through OpenRouter", "AgentIssue-Bench/SelfHeal/DeepSeek-V4.1-Flash/<tag>/rerun_<k>/run_record.json", "provider of the run step")
add("aib_gptoss_failed", aist["FAILED"], "gpt-oss-120b AgentIssue-Bench kept reruns SelfHeal marked FAILED", "AgentIssue-Bench/SelfHeal/gpt-oss-120b/<tag>/rerun_<k>/Fix-Agent/results", "Status line")

add("fix_plan_departure_numbers", "11, 12, 13, 14, 15, 16", "numbers of the fix plan departures the report cites above ten", "/home/grads/junh/.claude/plans/write-delivery-in-plan-bench-md-calm-clock.md", "numbered list under Departures from your instruction")

out = f"{H}/docs/selfheal_deployment_numbers.md"
with open(out, "w") as f:
    f.write("# Number registry, SelfHeal deployment report\n\nRows written by `docs/selfheal_deployment_numbers.py`. The report is checked with\n\n"
            "```\npython3 ~/.claude/skills/number-check/scripts/check_numbers.py --registry docs/selfheal_deployment_numbers.md "
            "--ignore '^7[6-9][0-9]{6},?$' --ignore '^[0-9]\\.[0-9]{1,2}$' --ignore '^2[56][0-9]{2}\\.[0-9]{5}$' --ignore '127\\.0\\.0\\.1' docs/selfheal_deployment.md\n```\n\n"
            "The ignore patterns skip the eight digit AgentDefect case ids, section numbers and two part versions such as 3.11 and 1.9, the arXiv ids, and the address 127.0.0.1.\n\n"
            "| name | value | what it counts | source file | how it is computed | date read |\n|---|---|---|---|---|---|\n")
    for r in rows:
        f.write("| " + " | ".join(r) + f" | {today} |\n")
print(len(rows), "rows")
for r in rows:
    print(r[0], r[1])
