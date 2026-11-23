#!/bin/bash
# The adapted SelfHeal configuration on AgentIssue-Bench for one ARC model (fix plan, departure 6, Jun "choice 2"):
# the repair loop with five reruns per issue, two at a time (Jun "reduce workload to 2"), then the one
# replacement of reruns whose search failed or that stopped. The model's rules, intents and file picks
# already exist and are reused unchanged, so they are not rebuilt here. AgentIssue-Bench runs on a
# different model from the one AgentDefect uses at the same time (Jun "if we start agent issuebench and
# the agent defect with different LLM model there is no workload confliction. please do this").
# Usage: setsid nohup bash run_adapted.sh gpt-oss-120b > ../run_adapted_gpt-oss-120b.log 2>&1 < /dev/null &
set -u
M="$1"
cd /data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/SelfHeal/code
PY=/data/wang/junh/envs/selfheal/bin/python
R="../$M/rules"
if [ ! -s "$R/fix_pattern_rules.csv" ] || [ ! -s "$R/test_descriptions_with_intent.csv" ]; then
  echo "rules or intents of $M missing, nothing run $(date -Is)"
  exit 1
fi
echo "pick start $M $(date -Is)"
"$PY" driver.py pick --model "$M"
echo "repair start $M $(date -Is)"
"$PY" driver.py repair --model "$M" --reruns 5 --parallel 2
echo "repair exit $? $(date -Is)"
echo "redo start $M $(date -Is)"
"$PY" driver.py redo --model "$M" --parallel 2
echo "redo exit $? $(date -Is)"
