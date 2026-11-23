"""Execute each issue's original code five times through the null patch, and the benchmark's test_buggy
diagnostic five times, with no run of the developer's fix (plan step 3k, Jun "i don't trust your generate
results of set 2. drop all", then "Skip them"). It is calibrate.py's own loop with the positive control and
the test_fixed runs left out. calibrate.py stays unchanged, and every record is written by its functions.

  python calibrate_original.py --model DeepSeek-V4.1-Flash
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calibrate as cal  # noqa: E402
import test_repairs as tr  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tags", nargs="*")
    ap.add_argument("--model", choices=tr.MODELS)
    a = ap.parse_args()
    models = [a.model] if a.model else tr.MODELS
    tags = a.tags or sorted(json.load(open(os.path.join(tr.INPUTS, "named_files.json"))))
    for tag in tags:
        evaluators = ["shipped"] + (["corrected"] if tag in tr.CORRECTIONS else [])
        plan = []
        for m in models:
            for ev in evaluators:
                for k in range(1, cal.RUNS + 1):
                    plan.append((m, ev, "negative", k))
            for k in range(1, cal.RUNS + 1):
                plan.append((m, "shipped", "diagnostic", k))
        todo = [p for p in plan if not os.path.exists(os.path.join(cal.CHECK, p[0], tag, f"{p[1]}_{p[2]}_{p[3]}", "test_record.json"))]
        if not todo:
            print(tag, "original-code runs done before", flush=True)
            continue
        image = tr.image_of(tag)
        pulled = image.startswith("alfin06/")
        if pulled:
            subprocess.run(["docker", "pull", "-q", image], check=True, capture_output=True)
        try:
            for m, ev, control, k in todo:
                out = os.path.join(cal.CHECK, m, tag, f"{ev}_{control}_{k}")
                extra = {"control": control, "run": k}
                if control == "diagnostic":
                    r = tr.run_eval(tag, image, m, out, ev, diagnostic=True, extra=extra)
                else:
                    r = tr.run_eval(tag, image, m, out, ev, patch_text=cal.NULL_PATCH, extra=extra)
                print(tag, m, ev, control, k, f"exit {r['exit']}" if r["passed"] is None else "passed" if r["passed"] else f"failed exit {r['exit']}",
                      r["seconds"], "s", time.strftime("%H:%M:%S"), flush=True)
        finally:
            if pulled:
                subprocess.run(["docker", "rmi", "-f", image], capture_output=True)
                print(tag, "image removed", flush=True)


if __name__ == "__main__":
    main()
