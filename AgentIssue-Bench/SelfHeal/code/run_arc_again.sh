#!/bin/bash
# The DeepSeek-V4.1-Flash reruns on AgentIssue-Bench that had not started, back on ARC (Jun "ok. let's
# switch back to arc"), after the OpenRouter run (run_openrouter.sh) was stopped. Reruns with a SelfHeal
# result are kept ("done before"). The reruns named as arguments, TAG:K, were still running on OpenRouter
# under the stopped driver when this run started, so they are skipped here. The rules, intents and file
# picks built on ARC are reused unchanged. Then the one redo, on ARC. Two reruns at a time (Jun "reduce
# workload to 2").
# Usage: setsid nohup bash run_arc_again.sh gpt-engineer_1197:1 lagent_239:1 >> ../run_DeepSeek-V4.1-Flash.log 2>&1 < /dev/null &
set -u
M=DeepSeek-V4.1-Flash
cd /data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/SelfHeal/code
PY=/data/wang/junh/envs/selfheal/bin/python
echo "arc again repair start $M, skipping $* $(date -Is)"
"$PY" driver.py repair --model "$M" --reruns 5 --parallel 2 --skip "$@"
echo "arc again repair exit $? $(date -Is)"
echo "arc again redo start $M $(date -Is)"
"$PY" driver.py redo --model "$M" --parallel 2
echo "arc again redo exit $? $(date -Is)"
