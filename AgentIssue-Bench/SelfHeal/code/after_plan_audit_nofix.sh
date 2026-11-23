#!/bin/bash
# Plan step 3k: the steps after_plan_audit.sh still had to run, with no run of the authors' fix
# (Jun "i don't trust your generate results of set 2. drop all", then "Skip them"). Same order and the same
# rules as after_plan_audit.sh: AgentDefect and AgentIssue-Bench never use the same ARC model at once, one
# test container and one environment at a time, a model is tested only after its repair run has ended.
#  1. DeepSeek-V4.1-Flash after run_arc_again.sh ends: AgentIssue-Bench original-code runs, the reruns with
#     the corrected test as input, the tests, the score, the score of both models, then its AgentDefect
#     original-program runs and any untested repair
#  2. GLM-5.3 after run_adapted.sh GLM-5.3 ends, the same steps
# Usage: setsid nohup bash after_plan_audit_nofix.sh > ../after_plan_audit_nofix.log 2>&1 < /dev/null &
set -u
H=/data/wang/junh/githubs/stochastic-harness
AI=$H/AgentIssue-Bench/SelfHeal/code
AD=$H/AgentDefect/SelfHeal/code
PY=/data/wang/junh/envs/selfheal/bin/python
PYAD=/data/wang/junh/python/cpython-3.10.19/bin/python3.10

wait_for() {
  echo "waiting while '$1' runs $(date -Is)"
  while pgrep -f "$1" > /dev/null; do sleep 120; done
  echo "'$1' ended $(date -Is)"
}

agentissue() {
  M="$1"
  cd "$AI"
  echo "$M AgentIssue-Bench original-code runs start $(date -Is)"
  "$PY" -u calibrate_original.py --model "$M"
  echo "$M AgentIssue-Bench original-code runs exit $? $(date -Is)"
  echo "$M corrected-input reruns start $(date -Is)"
  "$PY" -u driver.py repair --model "$M" --corrected-input --reruns 5 --parallel 2
  echo "$M corrected-input reruns exit $? $(date -Is)"
  echo "$M AgentIssue-Bench tests start $(date -Is)"
  "$PY" -u test_repairs.py --models "$M"
  echo "$M AgentIssue-Bench tests exit $? $(date -Is)"
  "$PY" score_tests.py --models "$M" > "../score_$M.txt" 2>&1
  echo "$M AgentIssue-Bench score exit $? $(date -Is)"
}

agentdefect_original() {
  M="$1"
  cd "$AD"
  echo "$M AgentDefect original-program runs start $(date -Is)"
  "$PYAD" -u test_original_and_repairs.py --models "$M"
  echo "$M AgentDefect original-program runs exit $? $(date -Is)"
}

echo "queue start $(date -Is)"
wait_for "run_arc_again.sh"
agentissue DeepSeek-V4.1-Flash
cd "$AI"
"$PY" score_tests.py --models gpt-oss-120b DeepSeek-V4.1-Flash > ../score_gpt-oss-120b_DeepSeek-V4.1-Flash.txt 2>&1
echo "score of both models exit $? $(date -Is)"
agentdefect_original DeepSeek-V4.1-Flash
wait_for "run_adapted.sh GLM-5.3"
agentissue GLM-5.3
agentdefect_original GLM-5.3
echo "queue end $(date -Is)"
