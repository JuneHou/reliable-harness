"""Why SelfHeal fails on AgentIssue-Bench's multi-file issues (plan "why SelfHeal fails on AgentIssue-Bench's
multi-file issues", step 1). Reads the records only and changes nothing.

The runs are SelfHeal adapted to several files (the named or picked files joined with "### <path>" lines,
run_agent_adapted.py, the FINAL CODE split back with a left-out file kept unchanged). Only the shipped
evaluator's records are read (Jun "you should never change evaluation code or file to make result
incomparable"). The developer patch counts the source files each fix touches, for this analysis only.

Per kept rerun <model>/<tag>/rerun_<k> it writes one row of multifile_analysis.csv. The issue's calibration
group for that model comes from AgentIssue-Bench/case_check/<model>/<tag>/shipped_negative_* and
shipped_positive_*: separates (null patch passes none, developer patch passes all), fails both, passes the
null patch (all null runs pass), or mixed.

The cause of a rerun's outcome is the first that applies.
  1 no repair: no input file, or no SelfHeal result
  2 the test fails both controls
  3 the test passes the null patch
  4 the test gives mixed controls
  In an issue whose test separates, a passing rerun is "the test passed". A failing one gets the first of
  5 SelfHeal did not get every file the fix touches (fix of one to seven source files only)
  6 the repair left out a file it got
  7 the patch did not apply ("Failed to apply patch", a failed hunk, a missing file, or no patch program)
  8 the repair changed fewer source files than the fix touches (fix of one to seven source files only)
  9 the test failed with the same last failure line as a null-patch run of that issue and model, after
    removing digits, paths and hexadecimal ids
  10 the test failed otherwise

  python analyze_multifile.py --models gpt-oss-120b DeepSeek-V4.1-Flash
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
ISSUES = os.path.join(ROOT, "inputs", "issues")
RERUNS = 5

TEST = re.compile(r"(^|/)(tests?|__tests__|testing|spec)/|(^|/)test_[^/]*$|_test\.[a-z]+$|\.(test|spec)\.[a-z]+$|(^|/)conftest\.py$")
DOC = re.compile(r"(^|/)(docs?|documentation|examples?|samples?|notebooks?|cookbook)/|\.(md|rst|ipynb|txt|png|jpg|svg)$")
CODE = re.compile(r"\.(py|ts|tsx|js|jsx|mjs|cjs|go|cs|java|rs|sh)$")
APPLY_FAIL = re.compile(r"Failed to apply patch|Hunk #\d+ FAILED|can't find file to patch|No file to patch|malformed patch|patch: \*\*\*\*")
NO_PATCH_PROGRAM = re.compile(r"patch: command not found|patch: not found")
FAILURE_LINE = re.compile(r"error|exception|fail|❌|traceback|assert|not verified|not confirmed|bug reproduced", re.I)

CAUSES = ["no repair", "test fails both controls", "test passes the null patch", "test gives mixed controls",
          "test passed", "did not get every file the fix touches", "left out a file it got", "patch did not apply",
          "changed fewer source files than the fix", "failed like the null patch", "failed otherwise"]


def source_files(paths):
    return [f for f in paths if CODE.search(f) and not TEST.search(f) and not DOC.search(f)]


def fix_files(tag):
    p = os.path.join(ISSUES, tag, "developer.patch")
    files = re.findall(r"^diff --git a/(\S+) b/", open(p, encoding="utf-8", errors="replace").read(), re.M)
    return source_files(files)


def fix_group(n):
    if n == 0:
        return "none"
    if n == 1:
        return "one"
    if n <= 7:
        return "two to seven"
    return "unknown"


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


def calibration(model, tag):
    def runs(control):
        return [json.load(open(p))["passed"] for p in glob.glob(os.path.join(CHECK, model, tag, f"shipped_{control}_*", "test_record.json"))]
    neg, pos = runs("negative"), runs("positive")
    if not neg or not pos:
        return "not calibrated", set()
    nulls = {last_failure_line(os.path.dirname(p)) for p in glob.glob(os.path.join(CHECK, model, tag, "shipped_negative_*", "test_record.json"))}
    if all(neg):
        return "passes the null patch", nulls
    if not any(neg) and all(pos):
        return "separates", nulls
    if not any(neg) and not any(pos):
        return "fails both", nulls
    return "mixed", nulls


def status_of(rerun, tag):
    m = re.search(r"(?m)^Status:\s*(\S+)", read(os.path.join(rerun, "Fix-Agent", "results", f"{tag}_result.txt")))
    return m.group(1) if m else "NO RESULT"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    models = ap.parse_args().models
    tags = sorted(json.load(open(os.path.join(ROOT, "inputs", "named_files.json"))))
    fixes = {t: fix_files(t) for t in tags}
    rows = []
    for m in models:
        for t in tags:
            group, nulls = calibration(m, t)
            need = fixes[t]
            fg = fix_group(len(need))
            for k in range(1, RERUNS + 1):
                d = os.path.join(ROOT, m, t, f"rerun_{k}")
                sent = json.load(open(os.path.join(d, "input_files.json"))) if os.path.exists(os.path.join(d, "input_files.json")) else {}
                files = sent.get("files", [])
                status = status_of(d, t)
                rp = os.path.join(d, "test", "test_record.json")
                rec = json.load(open(rp)) if os.path.exists(rp) else None
                passed = bool(rec and rec.get("passed"))
                note = str((rec or {}).get("split_note") or (rec or {}).get("not_run") or "")
                left_out = note.startswith("header missing") or note.startswith("several files sent")
                changed = source_files((rec or {}).get("changed") or [])
                log = read(os.path.join(d, "test", "test.log")) + read(os.path.join(d, "test", "test_stderr.log"))
                no_patch_program = bool(NO_PATCH_PROGRAM.search(log))
                not_applied = bool(APPLY_FAIL.search(log)) or no_patch_program
                got_all = ("n/a" if fg == "none" else "unknown" if fg == "unknown"
                           else "yes" if set(need) <= set(files) else "no")
                if os.path.exists(os.path.join(d, "no_input.json")) or status == "NO RESULT" or rec is None or (rec.get("not_run") and not left_out):
                    cause = "no repair"
                elif group == "fails both":
                    cause = "test fails both controls"
                elif group == "passes the null patch":
                    cause = "test passes the null patch"
                elif group == "mixed":
                    cause = "test gives mixed controls"
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
                elif last_failure_line(os.path.join(d, "test")) in nulls:
                    cause = "failed like the null patch"
                else:
                    cause = "failed otherwise"
                rows.append({"model": m, "tag": t, "rerun": k, "files_sent": len(files), "how": sent.get("how", ""),
                             "fix_source_files": len(need), "fix_group": fg, "got_every_fix_file": got_all,
                             "left_out_a_file": left_out, "repair_source_files_changed": len(changed),
                             "patch_not_applied": not_applied, "no_patch_program": no_patch_program,
                             "status": status, "test_passed": passed, "calibration_group": group, "cause": cause})
    out = os.path.join(ROOT, "multifile_analysis.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows written to {out}")
    for m in models:
        mine = [r for r in rows if r["model"] == m]
        print(f"\n{m}, {len(mine)} kept reruns, cause by SelfHeal's status")
        print("| cause | reruns | ACCEPTED | FAILED | no result |\n|---|---|---|---|---|")
        for c in CAUSES:
            sub = [r for r in mine if r["cause"] == c]
            st = collections.Counter(r["status"] for r in sub)
            print(f"| {c} | {len(sub)} | {st['ACCEPTED']} | {st['FAILED']} | {len(sub) - st['ACCEPTED'] - st['FAILED']} |")
        print(f"\n{m}, issues whose shipped test separates, by the source files the fix touches")
        print("| fix touches | issues | reruns | got every fix file | passed |\n|---|---|---|---|---|")
        sep = [r for r in mine if r["calibration_group"] == "separates"]
        for g in ("one", "two to seven", "unknown", "none"):
            sub = [r for r in sep if r["fix_group"] == g]
            print(f"| {g} | {len({r['tag'] for r in sub})} | {len(sub)} | {sum(r['got_every_fix_file'] == 'yes' for r in sub)} | {sum(r['test_passed'] for r in sub)} |")
        multi = [r for r in mine if r["files_sent"] > 1 and r["status"] != "NO RESULT"]
        lo = [r for r in multi if r["left_out_a_file"]]
        st = collections.Counter(r["status"] for r in lo)
        print(f"\n{m}, reruns sent two or more files: {len(multi)}, final code left out a file in {len(lo)}, "
              f"of which ACCEPTED {st['ACCEPTED']} and FAILED {st['FAILED']}")


if __name__ == "__main__":
    main()
