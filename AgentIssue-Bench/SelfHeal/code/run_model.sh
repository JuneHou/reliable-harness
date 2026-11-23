#!/bin/bash
# Run SelfHeal on AgentIssue-Bench for one ARC model: the fix rules and intents, the file picking,
# the repair loop with five reruns, then the one redo of stopped and search-failed reruns.
# Every step resumes. Finished summaries, rules, intents, picks and reruns are kept and not redone.
# Usage: setsid nohup bash run_model.sh gpt-oss-120b > ../run_gpt-oss-120b.log 2>&1 < /dev/null &
set -u
M="$1"
cd /data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/SelfHeal/code
PY=/data/wang/junh/envs/selfheal/bin/python
echo "rules start $M $(date -Is)"
"$PY" driver.py rules --model "$M"
RC=$?
echo "rules exit $RC $(date -Is)"
R="../$M/rules"
if [ "$RC" -ne 0 ] || [ ! -s "$R/fix_pattern_rules.csv" ] || [ ! -s "$R/test_descriptions_with_intent.csv" ]; then
  echo "rules step failed or its output is missing, nothing more run $(date -Is)"
  exit 1
fi
echo "pick start $M $(date -Is)"
"$PY" driver.py pick --model "$M"
echo "pick exit $? $(date -Is)"
echo "repair start $M $(date -Is)"
"$PY" driver.py repair --model "$M" --reruns 5 --parallel 2
echo "repair exit $? $(date -Is)"
echo "redo start $M $(date -Is)"
"$PY" driver.py redo --model "$M" --parallel 2
echo "redo exit $? $(date -Is)"
