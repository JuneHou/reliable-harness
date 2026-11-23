#!/usr/bin/env python3
"""HarnessFix inputs for AgentDefect (plan step 2).

For each case, the harness folder HarnessFix may read and edit: the case's files from SelfHeal's
AgentDefect.zip without run_fixed.py (the reference fix), test.py (the test), readme.md (it names the
Stack Overflow post that holds the fix) and output.log. hf-26 gets the rebuilt run_buggy.py of
Plan_bench.md. The task text is the code intent SelfHeal received for the case and model
(SelfHeal run_agent.py:292 uses row['intent']), read from that model's rules folder.

Writes inputs/programs/<case>/ and inputs/<model>/tasks.jsonl, and lists every file copied.
"""
import argparse
import csv
import json
import os
import shutil
import sys
import zipfile

H = "/data/wang/junh/githubs/stochastic-harness/AgentDefect"
OUT = os.path.join(H, "HarnessFix", "inputs")
ZIP = "/data/wang/junh/githubs/SelfHeal/AgentDefect.zip"
HF26 = os.path.join(H, "SelfHeal", "inputs", "hf-26_run_buggy.py")
LEFT_OUT = {"run_fixed.py", "test.py", "readme.md", "output.log", "test_output.json"}  # test_output.json: written by test.py (79343179), not read by the program


def case_files(z):
    out = {}
    for p in z.namelist():
        parts = p.split("/")
        if p.startswith("__MACOSX") or len(parts) < 3 or not parts[-1] or parts[-1].startswith("._"):
            continue
        out.setdefault(parts[1], []).append(p)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    a = ap.parse_args()
    z = zipfile.ZipFile(ZIP)
    listing = {}
    for case, paths in sorted(case_files(z).items()):
        dest = os.path.join(OUT, "programs", case)
        shutil.rmtree(dest, ignore_errors=True)
        copied, skipped = [], []
        for p in paths:
            rel = "/".join(p.split("/")[2:])
            if rel in LEFT_OUT:
                skipped.append(rel)
                continue
            target = os.path.join(dest, rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "wb") as f:
                f.write(z.read(p))
            copied.append(rel)
        if case == "hf-26":
            shutil.copy(HF26, os.path.join(dest, "run_buggy.py"))
            copied.append("run_buggy.py (rebuilt, Plan_bench.md)")
        if not os.path.exists(os.path.join(dest, "run_buggy.py")):
            sys.exit(f"{case}: no run_buggy.py")
        listing[case] = {"copied": sorted(copied), "left_out": sorted(skipped)}
    json.dump(listing, open(os.path.join(OUT, "programs_listing.json"), "w"), indent=1)
    for m in a.models:
        src = os.path.join(H, "SelfHeal", m, "rules", "test_descriptions_with_intent.csv")
        rows = {r["id"]: r["intent"] for r in csv.DictReader(open(src, encoding="utf-8"))}
        missing = sorted(set(listing) - set(rows))
        os.makedirs(os.path.join(OUT, m), exist_ok=True)
        with open(os.path.join(OUT, m, "tasks.jsonl"), "w", encoding="utf-8") as f:
            for case in sorted(listing):
                if case in rows:
                    f.write(json.dumps({"task_id": case, "instruction": rows[case]}, ensure_ascii=False) + "\n")
        print(m, "intents", len(rows), "cases without an intent", missing)
    print("programs", len(listing), "files left out per case", sorted({x for v in listing.values() for x in v["left_out"]}))


if __name__ == "__main__":
    main()
