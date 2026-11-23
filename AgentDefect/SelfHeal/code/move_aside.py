"""Move a model's reruns that cannot be kept out of the way, so that driver.py redoes them.

  search failed  a tool reply in the rerun contains "Search error", our DuckDuckGo search failing
  stopped        the rerun has no result file, because its run was stopped before it finished

They go to <model>/_search_failed/<case>/rerun_<k> and <model>/_stopped/<case>/rerun_<k>.
A folder already there keeps its place and the new one gets a suffix _2, _3 and so on.

  python move_aside.py GLM-5.3           move them
  python move_aside.py GLM-5.3 --check   only count them
"""
import glob
import json
import os
import shutil
import subprocess
import sys

ROOT = "/data/wang/junh/githubs/stochastic-harness/AgentDefect/SelfHeal"


def search_failed(rerun):
    log = os.path.join(rerun, "relay_log_run_agent.jsonl")
    if not os.path.exists(log):
        return False
    for line in open(log, encoding="utf-8"):
        for msg in json.loads(line)["request"].get("messages", []):
            if msg.get("role") == "tool" and "Search error" in str(msg.get("content")):
                return True
    return False


def main():
    model, check = sys.argv[1], "--check" in sys.argv
    if not check and subprocess.run(["pgrep", "-f", f"[d]river.py repair --model {model}"],
                                    capture_output=True).returncode == 0:
        raise SystemExit(f"the {model} repair is still running, nothing moved")
    found = {"_search_failed": [], "_stopped": []}
    for rerun in sorted(glob.glob(os.path.join(ROOT, model, "[0-9h]*", "rerun_*"))):
        case, k = rerun.split("/")[-2:]
        if not os.path.exists(os.path.join(rerun, "Fix-Agent", "results", f"{case}_result.txt")):
            found["_stopped"].append(rerun)
        elif search_failed(rerun):
            found["_search_failed"].append(rerun)
    for where, reruns in found.items():
        print(model, where, len(reruns), " ".join("/".join(r.split("/")[-2:]) for r in reruns), flush=True)
        if check:
            continue
        for rerun in reruns:
            case, k = rerun.split("/")[-2:]
            dest, i = os.path.join(ROOT, model, where, case, k), 1
            while os.path.exists(dest):
                i += 1
                dest = os.path.join(ROOT, model, where, case, f"{k}_{i}")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.move(rerun, dest)


if __name__ == "__main__":
    main()
