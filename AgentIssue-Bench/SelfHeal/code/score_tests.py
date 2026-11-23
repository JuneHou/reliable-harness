"""Score SelfHeal's AgentIssue-Bench repair tests, adapted configuration, as
AgentDefect/SelfHeal/code/score_tests.py does.

A planned repetition is rerun k of an issue and model, one run of the repair loop under a fixed setup
(rules, intents and file selections built once per model). It succeeds when SelfHeal marked it
ACCEPTED and its repair passed the issue's test, a test-passing (plausible) repair. Each table is given
twice, under the shipped evaluator and under the corrected evaluator (the shipped one for the issues
without a correction). First-attempt and final-policy success use the same planned repetitions, with
at most one replacement each.

Tables, each on its own:
  1. final-policy success per model and the number of issues with 0 to 5 successful reruns
  2. first-attempt success, the same way
  3. the four outcomes, SelfHeal's status by test pass or fail, final policy
  4. replacements and the model calls their first attempts cost
  5. calibration per issue and model, pass counts of the negative and positive controls under each
     evaluator and of the test_buggy diagnostic. A pass of the negative control, the unmodified buggy
     code, is self-recovery (Plan_bench.md decision "unrepaired harness passing on rerun", fix plan
     departure 16), and calibration.csv lists every control run with that flag
  6. the reruns with the corrected test as SelfHeal's input (fix plan departure 14), under the corrected
     evaluator, beside the kept reruns of the same issues under the same evaluator
Each CSV row also names the files the repair changes, as its test record gives them (Plan_bench.md step
"Rerun each method on each case", fix plan departure 16).
The 21 reruns of the first adaptation in <model>/_initial_adaptation/ are left out.

  python score_tests.py [--models MODEL ...]
"""
import argparse
import collections
import csv
import glob
import json
import os
import re

ROOT = "/data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/SelfHeal"
CHECK = "/data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/case_check"
MODELS = ["gpt-oss-120b", "GLM-5.3", "DeepSeek-V4.1-Flash"]
RERUNS = 5
CORRECTIONS = json.load(open(os.path.join(ROOT, "evaluator", "corrections.json")))


def status_of(folder, tag):
    res = os.path.join(folder, "Fix-Agent", "results", f"{tag}_result.txt")
    if not os.path.exists(res):
        return "NO RESULT"
    return re.search(r"(?m)^Status:\s*(\S+)", open(res, encoding="utf-8").read()).group(1)


def rec_of(folder, evaluator, tag):
    sub = "test_corrected" if evaluator == "corrected" and tag in CORRECTIONS else "test"
    p = os.path.join(folder, sub, "test_record.json")
    return json.load(open(p)) if os.path.exists(p) else None


def calls(folder):
    p = os.path.join(folder, "relay_log_run_agent.jsonl")
    return sum(1 for _ in open(p)) if os.path.exists(p) else 0


def firsts(model, tag, k):
    out = []
    for where in ("_search_failed", "_stopped"):
        out += glob.glob(os.path.join(ROOT, model, where, tag, f"rerun_{k}")) + \
               glob.glob(os.path.join(ROOT, model, where, tag, f"rerun_{k}_*"))
    return sorted(out, key=os.path.getmtime)


def table(title, header, lines):
    print(f"\n{title}")
    print("| " + " | ".join(header) + " |")
    print("|" + "---|" * len(header))
    for l in lines:
        print("| " + " | ".join(str(x) for x in l) + " |")


def changed(rec):
    if rec is None:
        return "no test record"
    if rec.get("not_run"):
        return "not tested: " + rec["not_run"]
    return "; ".join(rec.get("changed") or []) or "none"


CORRECTED_INPUT = ["ai_4411", "ai_5628", "ai_6510", "crewai_1532", "haystack_8912", "haystack_9523"]   # driver.py


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", default=MODELS)
    MODELS_RUN = ap.parse_args().models
    tags = sorted(json.load(open(os.path.join(ROOT, "inputs", "named_files.json"))))
    rows, missing = [], []
    for ev in ("shipped", "corrected"):
        for m in MODELS_RUN:
            for t in tags:
                for k in range(1, RERUNS + 1):
                    kept = os.path.join(ROOT, m, t, f"rerun_{k}")
                    fs = firsts(m, t, k)
                    first = fs[0] if fs else kept
                    kr, fr = rec_of(kept, ev, t), rec_of(first, ev, t)
                    if kr is None or fr is None:
                        missing.append(f"{ev} {m}/{t}/rerun_{k}")
                        continue
                    ks, fst = status_of(kept, t), status_of(first, t)
                    rows.append({"evaluator": ev, "model": m, "tag": t, "rerun": k, "final_status": ks,
                                 "final_test_passed": kr["passed"], "final_success": ks == "ACCEPTED" and kr["passed"],
                                 "replacements": len(fs), "first_attempt": os.path.relpath(first, ROOT),
                                 "first_status": fst, "first_test_passed": fr["passed"],
                                 "first_success": fst == "ACCEPTED" and fr["passed"],
                                 "first_attempt_calls": sum(calls(f) for f in fs),
                                 "final_changed_files": changed(kr), "first_changed_files": changed(fr)})
    if missing:
        raise SystemExit(f"{len(missing)} test records missing, first: {missing[:3]}")
    out = os.path.join(ROOT, "test_scores.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows written to {out}")
    n = len(tags) * RERUNS
    for ev in ("shipped", "corrected"):
        R = [r for r in rows if r["evaluator"] == ev]
        for key, title in [("final_success", "Final-policy success"), ("first_success", "First-attempt success")]:
            lines = []
            for m in MODELS_RUN:
                mine = [r for r in R if r["model"] == m]
                per = collections.Counter()
                for r in mine:
                    per[r["tag"]] += r[key]
                dist = collections.Counter(per[t] for t in tags)
                lines.append([m, len(mine), sum(r[key] for r in mine)] + [dist[i] for i in range(RERUNS + 1)])
            table(f"{title}, {ev} evaluator, {len(tags)} issues, {RERUNS} planned repetitions each",
                  ["model", "planned repetitions", "successes"] + [f"issues with {i}" for i in range(RERUNS + 1)], lines)
        lines = []
        for m in MODELS_RUN:
            cnt = collections.Counter((r["final_status"], r["final_test_passed"]) for r in R if r["model"] == m)
            lines.append([m, cnt[("ACCEPTED", True)], cnt[("ACCEPTED", False)], cnt[("FAILED", True)],
                          cnt[("FAILED", False)], sum(v for (s, _), v in cnt.items() if s not in ("ACCEPTED", "FAILED"))])
        table(f"Four outcomes, final policy, {ev} evaluator, {n} planned repetitions per model",
              ["model", "ACCEPTED, pass", "ACCEPTED, fail", "FAILED, pass", "FAILED, fail", "no result"], lines)
    lines = []
    for m in MODELS_RUN:
        mine = [r for r in rows if r["model"] == m and r["evaluator"] == "shipped"]
        lines.append([m, sum(r["replacements"] > 0 for r in mine), sum(r["replacements"] > 1 for r in mine),
                      sum(r["first_attempt_calls"] for r in mine)])
    table(f"Replacements, {n} planned repetitions per model",
          ["model", "repetitions replaced", "replaced more than once", "model calls of replaced first attempts"], lines)
    lines, crows = [], []
    for t in tags:
        for m in MODELS_RUN:
            cell = []
            for ev in ("shipped", "corrected"):
                for control in ("negative", "positive"):
                    recs = [json.load(open(p)) for p in glob.glob(os.path.join(CHECK, m, t, f"{ev}_{control}_*", "test_record.json"))]
                    cell.append(f"{sum(r['passed'] for r in recs)} of {len(recs)}" if recs else "none")
                    crows += [{"model": m, "tag": t, "evaluator": ev, "control": control, "run": r["run"], "passed": r["passed"],
                               "self_recovery": control == "negative" and r["passed"]} for r in sorted(recs, key=lambda r: r["run"])]
            recs = [json.load(open(p)) for p in glob.glob(os.path.join(CHECK, m, t, "shipped_diagnostic_*", "test_record.json"))]
            cell.append(f"{sum(r['exit'] == 0 for r in recs)} of {len(recs)}" if recs else "none")
            lines.append([t, m] + cell)
    with open(os.path.join(ROOT, "calibration.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["model", "tag", "evaluator", "control", "run", "passed", "self_recovery"])
        w.writeheader()
        w.writerows(crows)
    table("Calibration, passes of the negative control (buggy code) and the positive control (developer patch). "
          "A pass of the negative control is self-recovery",
          ["issue", "model", "shipped negative (self-recovery)", "shipped positive", "corrected negative (self-recovery)",
           "corrected positive", "test_buggy exit 0"], lines)
    lines = []
    for m in MODELS_RUN:
        got = {}
        for which, base in (("shipped input", os.path.join(ROOT, m)), ("corrected input", os.path.join(ROOT, m, "_corrected_input"))):
            ok = n_rec = 0
            for t in CORRECTED_INPUT:
                for k in range(1, RERUNS + 1):
                    d = os.path.join(base, t, f"rerun_{k}")
                    r = rec_of(d, "corrected", t)
                    if r is None:
                        continue
                    n_rec += 1
                    ok += status_of(d, t) == "ACCEPTED" and r["passed"]
            got[which] = f"{ok} of {n_rec}" if n_rec else "not tested yet"
        lines.append([m, got["shipped input"], got["corrected input"]])
    table(f"Corrected evaluator, the {len(CORRECTED_INPUT)} issues of departure 14, successes of the kept reruns",
          ["model", "SelfHeal read the shipped test", "SelfHeal read the corrected test"], lines)


if __name__ == "__main__":
    main()
