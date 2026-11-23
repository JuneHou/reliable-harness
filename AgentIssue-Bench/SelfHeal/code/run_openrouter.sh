#!/bin/bash
# The DeepSeek-V4.1-Flash reruns on AgentIssue-Bench that had not started on ARC, run through OpenRouter
# with its default routing (Jun "let's try with open router for deep seek", "Default routing", "2").
# The rules, intents and file picks built on ARC are reused unchanged. Reruns with a SelfHeal result are
# kept ("done before"). ai_4411 and ai_6510 rerun 1 were still running under the stopped ARC driver
# when this run started, so they are skipped here. Then the one redo, also through OpenRouter. Two
# reruns at a time (Jun "reduce workload to 2").
# Usage: setsid nohup bash run_openrouter.sh >> ../run_DeepSeek-V4.1-Flash.log 2>&1 < /dev/null &
set -u
M=DeepSeek-V4.1-Flash
cd /data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/SelfHeal/code
PY=/data/wang/junh/envs/selfheal/bin/python
echo "openrouter repair start $M $(date -Is)"
"$PY" driver.py repair --model "$M" --reruns 5 --parallel 2 --provider openrouter --skip ai_4411:1 ai_6510:1
echo "openrouter repair exit $? $(date -Is)"
echo "openrouter redo start $M $(date -Is)"
"$PY" driver.py redo --model "$M" --parallel 2 --provider openrouter
echo "openrouter redo exit $? $(date -Is)"
