"""Score SelfHeal's AgentDefect repair tests.

A rerun is one run of SelfHeal's repair loop under a fixed setup: the model's rules and intents are
built once and every rerun reuses them. A planned repetition is rerun k of a case and model. It
succeeds when SelfHeal marked it ACCEPTED and its repair's test.py exited with 0, a test-passing
(plausible) repair. A FAILED rerun is not a success whatever its test gave.

A planned repetition whose first attempt was moved aside (search failed or stopped) has at most one
replacement (Jun "allow at most one replacement per original planned repetition"). First-attempt
success uses the first attempt, final-policy success uses the kept rerun, both over the same planned
repetitions (Jun "Calculate first-attempt and final-policy success over the same planned
repetitions").

Writes test_scores.csv, one row per planned repetition, and prints, each table on its own:
  1. final-policy success per model, and the number of cases with 0 to 5 successful reruns
  2. first-attempt success per model, the same way
  3. the four outcomes per model, SelfHeal's status by test pass or fail, final policy
  4. replacements per model and the model calls their first attempts cost
  5. calibration, per case and model, test passes of the archive's buggy and fixed program. A pass of
     the unmodified buggy code is self-recovery (Plan_bench.md decision "unrepaired harness passing on
     rerun", fix plan departure 16)
Cases in DROPPED stay in the CSV and are left out of tables 1 to 4.

Each CSV row also names the functions the repair changes (Plan_bench.md step "Rerun each method on each
case", "the files it changes", fix plan departure 16). A SelfHeal repair on AgentDefect is the whole of
run_fixed.py, so the file is always the program, and the row lists each top-level function, class
method and the module-level code whose source text differs from the case's run_buggy.py, with
functions only in one of the two marked added or removed. Writes calibration.csv, one row per
calibration run, with its self-recovery flag.

  python score_tests.py
"""
import ast
import collections
import csv
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_repairs import CALIB_LEFT_OUT, CALIB_ROOT, CALIB_RUNS, INPUTS, LISTS, MODELS, RERUNS, ROOT  # noqa: E402

# 79776520 needs a Google key and a Tavily key, which we do not have. Jun "for question 2, drop".
DROPPED = {"79776520": "needs GOOGLE_API_KEY and TAVILY_API_KEY (its readme), which we do not have"}


def code_units(src):
    """Source text of each top-level function, each class method and the module-level code, by name."""
    tree = ast.parse(src)
    units, module = {}, []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            units[node.name] = ast.get_source_segment(src, node)
        elif isinstance(node, ast.ClassDef):
            rest = []
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    units[f"{node.name}.{sub.name}"] = ast.get_source_segment(src, sub)
                else:
                    rest.append(ast.get_source_segment(src, sub) or "")
            units[f"{node.name}.<class body>"] = "\n".join(rest)
        else:
            module.append(ast.get_source_segment(src, node) or "")
    units["<module>"] = "\n".join(module)
    return units


def changed_functions(folder):
    """The repair's changed units against run_buggy.py in the test folder, or why they cannot be read."""
    t = os.path.join(folder, "test")
    fixed, buggy = os.path.join(t, "run_fixed.py"), os.path.join(t, "run_buggy.py")
    if not os.path.exists(buggy) and os.path.basename(os.path.dirname(folder)) == "hf-26":
        buggy = os.path.join(INPUTS, "hf-26_run_buggy.py")   # the archive ships none, the test folder keeps none
    if not (os.path.exists(fixed) and os.path.exists(buggy)):
        return "no repair file"
    try:
        new = code_units(open(fixed, encoding="utf-8").read())
    except SyntaxError:
        return "repair does not parse"
    old = code_units(open(buggy, encoding="utf-8").read())
    out = [n for n in sorted(set(old) & set(new)) if old[n] != new[n]]
    out += [f"{n} added" for n in sorted(set(new) - set(old))]
    out += [f"{n} removed" for n in sorted(set(old) - set(new))]
    return "; ".join(out) if out else "none"


def status_of(folder, case):
    res = os.path.join(folder, "Fix-Agent", "results", f"{case}_result.txt")
    if not os.path.exists(res):
        return "NO RESULT"
    return re.search(r"(?m)^Status:\s*(\S+)", open(res, encoding="utf-8").read()).group(1)


def test_of(folder):
    p = os.path.join(folder, "test", "test_record.json")
    return json.load(open(p)) if os.path.exists(p) else None


def calls(folder):
    p = os.path.join(folder, "relay_log_run_agent.jsonl")
    return sum(1 for _ in open(p)) if os.path.exists(p) else 0


def first_attempt(model, case, k):
    found = []
    for where in ("_search_failed", "_stopped"):
        for d in glob.glob(os.path.join(ROOT, model, where, case, f"rerun_{k}")) + \
                 glob.glob(os.path.join(ROOT, model, where, case, f"rerun_{k}_*")):
            found.append(d)
    return sorted(found, key=os.path.getmtime)


def table(title, header, lines):
    print(f"\n{title}")
    print("| " + " | ".join(header) + " |")
    print("|" + "---|" * len(header))
    for l in lines:
        print("| " + " | ".join(str(x) for x in l) + " |")


def main():
    cases = sorted(c for cs in LISTS.values() for c in cs)
    rows, missing = [], []
    for m in MODELS:
        for c in cases:
            for k in range(1, RERUNS + 1):
                kept = os.path.join(ROOT, m, c, f"rerun_{k}")
                kt = test_of(kept)
                if kt is None:
                    missing.append(f"{m}/{c}/rerun_{k}")
                    continue
                firsts = first_attempt(m, c, k)
                first = firsts[0] if firsts else kept
                ft = test_of(first)
                if ft is None:
                    missing.append(os.path.relpath(first, ROOT))
                    continue
                ks, fs = status_of(kept, c), status_of(first, c)
                rows.append({"model": m, "case": c, "rerun": k, "in_table": c not in DROPPED,
                             "final_status": ks, "final_test_passed": kt["passed"],
                             "final_success": ks == "ACCEPTED" and kt["passed"],
                             "replaced": bool(firsts), "replacements": len(firsts),
                             "first_attempt": os.path.relpath(first, ROOT), "first_status": fs,
                             "first_test_passed": ft["passed"], "first_success": fs == "ACCEPTED" and ft["passed"],
                             "first_attempt_calls": sum(calls(f) for f in firsts),
                             "final_changed_functions": changed_functions(kept),
                             "first_changed_functions": changed_functions(first)})
    if missing:
        raise SystemExit(f"{len(missing)} test records missing, first: {missing[:3]}")
    out = os.path.join(ROOT, "test_scores.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows written to {out}")
    tcases = [c for c in cases if c not in DROPPED]
    n = len(tcases) * RERUNS

    for key, title in [("final_success", "1. Final-policy success"), ("first_success", "2. First-attempt success")]:
        lines = []
        for m in MODELS:
            mine = [r for r in rows if r["model"] == m and r["in_table"]]
            per = collections.Counter()
            for r in mine:
                per[r["case"]] += r[key]
            dist = collections.Counter(per[c] for c in tcases)
            lines.append([m, len(mine), sum(r[key] for r in mine)] + [dist[i] for i in range(RERUNS + 1)])
        table(f"{title}, test-passing ACCEPTED repairs, {len(tcases)} cases, {RERUNS} planned repetitions each",
              ["model", "planned repetitions", "successes"] + [f"cases with {i}" for i in range(RERUNS + 1)], lines)

    lines = []
    for m in MODELS:
        mine = [r for r in rows if r["model"] == m and r["in_table"]]
        cnt = collections.Counter((r["final_status"], r["final_test_passed"]) for r in mine)
        lines.append([m, cnt[("ACCEPTED", True)], cnt[("ACCEPTED", False)], cnt[("FAILED", True)],
                      cnt[("FAILED", False)], sum(v for (s, _), v in cnt.items() if s not in ("ACCEPTED", "FAILED"))])
    table(f"3. Four outcomes, final policy, {n} planned repetitions per model",
          ["model", "ACCEPTED, pass", "ACCEPTED, fail", "FAILED, pass", "FAILED, fail", "no result"], lines)

    lines = []
    for m in MODELS:
        mine = [r for r in rows if r["model"] == m and r["in_table"]]
        lines.append([m, sum(r["replaced"] for r in mine), sum(r["replacements"] > 1 for r in mine),
                      sum(r["first_attempt_calls"] for r in mine)])
    table(f"4. Replacements, {n} planned repetitions per model",
          ["model", "repetitions replaced", "repetitions replaced more than once", "model calls of replaced first attempts"], lines)

    lines, crows = [], []
    for c in sorted(set(cases) - CALIB_LEFT_OUT):
        for m in MODELS:
            got = {}
            for which in ("buggy", "fixed"):
                recs = sorted((json.load(open(p)) for p in glob.glob(os.path.join(CALIB_ROOT, m, c, f"{which}_*", "test_record.json"))),
                              key=lambda r: r["run"])
                got[which] = f"{sum(r['passed'] for r in recs)} of {len(recs)}" if recs else "not run yet"
                crows += [{"model": m, "case": c, "program": which, "run": r["run"], "passed": r["passed"],
                           "self_recovery": which == "buggy" and r["passed"]} for r in recs]
            lines.append([c, m, got["buggy"], got["fixed"]])
    with open(os.path.join(ROOT, "calibration.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["model", "case", "program", "run", "passed", "self_recovery"])
        w.writeheader()
        w.writerows(crows)
    table(f"5. Calibration, test passes of the archive's programs, {CALIB_RUNS} runs each. "
          "A pass of the buggy program is self-recovery",
          ["case", "model", "buggy program passes (self-recovery)", "fixed program passes"], lines)
    print(f"\nTables 1 to 4 leave out:")
    for c, why in DROPPED.items():
        print(f"  {c}: {why}")


if __name__ == "__main__":
    main()
