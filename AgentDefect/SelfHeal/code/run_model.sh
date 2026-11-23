#!/bin/bash
# Run SelfHeal for one ARC model: the fix rules and intents, then the repair loop.
# Every step resumes. Finished summaries, rules, intents and reruns are kept and not redone.
# Usage: setsid nohup bash run_model.sh gpt-oss-120b > ../run_gpt-oss-120b.log 2>&1 < /dev/null &
set -u
M="$1"
cd /data/wang/junh/githubs/stochastic-harness/AgentDefect/SelfHeal/code
PY=/data/wang/junh/envs/selfheal/bin/python
echo "rules start $M $(date -Is)"
"$PY" driver.py rules --model "$M"
RC=$?
echo "rules exit $RC $(date -Is)"
R="../$M/rules"
if [ "$RC" -eq 0 ] && [ -s "$R/fix_pattern_rules.csv" ] && [ -s "$R/test_descriptions_with_intent.csv" ]; then
  echo "repair start $M $(date -Is)"
  "$PY" driver.py repair --model "$M" --reruns 5 --parallel 5
  echo "repair exit $? $(date -Is)"
else
  echo "rules step failed or its output is missing, repair not started $(date -Is)"
fi
