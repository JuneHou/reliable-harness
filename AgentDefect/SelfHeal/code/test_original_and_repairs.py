"""Test every SelfHeal repair and execute each case's original program five times, with no run of the
authors' fixed program (plan step 3k, Jun "i don't trust your generate results of set 2. drop all", then
"Skip them"). It is test_repairs.py's own loop with the fixed program left out. test_repairs.py stays
unchanged, and every record is written by its own functions, so the records stay comparable.

  python test_original_and_repairs.py --models DeepSeek-V4.1-Flash
"""
import argparse
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_repairs as tr  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lists", nargs="*", type=int)
    ap.add_argument("--models", nargs="*", default=tr.MODELS)
    a = ap.parse_args()
    calib_cases = set(tr.case_ids()) - tr.CALIB_LEFT_OUT
    sizes = tr.check_lists()
    tr.check_split()
    envs = tr.environments()
    print("lists checked:", len(tr.LISTS), "lists,", sum(map(len, tr.LISTS.values())), "cases, pins per list",
          sizes, "| environments", [(e, len(cs)) for e, _, cs, _ in envs], flush=True)
    for env_name, n, cases, pins in envs:
        if a.lists and n not in a.lists:
            continue
        waiting = [f"{m}/{c}/rerun_{k}" for c in cases for m in tr.MODELS for k in range(1, tr.RERUNS + 1)
                   if not os.path.exists(os.path.join(tr.ROOT, m, c, f"rerun_{k}", "Fix-Agent", "results", f"{c}_result.txt"))]
        if waiting:
            print("env", env_name, "deferred, reruns without a result:", " ".join(waiting), flush=True)
            continue
        todo = []
        for c in sorted(cases):
            for m in a.models:
                for k in range(1, tr.RERUNS + 1):
                    if not os.path.exists(os.path.join(tr.ROOT, m, c, f"rerun_{k}", "test", "test_record.json")):
                        todo.append((f"{c} {m} {k}", tr.test_one, (m, c, k)))
                for d in tr.first_attempts(m, c):
                    if not os.path.exists(os.path.join(d, "test", "test_record.json")):
                        todo.append((f"{c} {m} first {os.path.relpath(d, tr.ROOT)}", tr.test_first, (m, c, d)))
                if c in calib_cases:
                    for k in range(1, tr.CALIB_RUNS + 1):   # the original program only, no fixed program
                        if not os.path.exists(os.path.join(tr.CALIB_ROOT, m, c, f"buggy_{k}", "test_record.json")):
                            todo.append((f"{c} {m} original program {k}", tr.test_calib, (m, c, "buggy", k)))
        if not todo:
            print("env", env_name, "all tests done before", flush=True)
            continue
        print("env", env_name, "building", time.strftime("%H:%M:%S"), flush=True)
        try:
            env_rec, py = tr.build_env(env_name, n, cases, pins)
            print("env", env_name, "environment", env_rec["install"], "|", env_rec["seconds"], "s", flush=True)
            for label, fn, args in todo:
                print("env", env_name, label, fn(*args, py, env_rec), time.strftime("%H:%M:%S"), flush=True)
        finally:
            shutil.rmtree(os.path.join(tr.TEST_ENVS, f"list_{env_name}"), ignore_errors=True)
            print("env", env_name, "environment deleted", flush=True)


if __name__ == "__main__":
    main()
