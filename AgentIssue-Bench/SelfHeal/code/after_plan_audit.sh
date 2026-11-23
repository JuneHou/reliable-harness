#!/bin/bash
# Fix plan departure 16 (Jun "now. fix everything you didn't follow the plan"): the steps still open, in an
# order that keeps the plan's rules. AgentDefect and AgentIssue-Bench never use the same ARC model at once,
# one AgentIssue-Bench test container at a time, one AgentDefect environment at a time, a model is calibrated
# and tested only after its repair run has ended (departure 11), two SelfHeal reruns at a time.
#  1. wait for the AgentDefect calibration of gpt-oss-120b (test_repairs.py --models gpt-oss-120b), then run
#     it once more, which skips every finished record and resumes it if it stopped early
#  2. AgentIssue-Bench, per model: calibration (departure 4), the reruns with the corrected test as input
#     (departure 14), the tests of every kept rerun, first attempt and corrected-input rerun under both
#     evaluators, the score
#  3. gpt-oss-120b first, then DeepSeek-V4.1-Flash after run_arc_again.sh ends, then GLM-5.3 after
#     run_adapted.sh GLM-5.3 ends, each followed by its AgentDefect calibration
# Usage: setsid nohup bash after_plan_audit.sh > ../after_plan_audit.log 2>&1 < /dev/null &
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
  echo "$M AgentIssue-Bench calibration start $(date -Is)"
  "$PY" -u calibrate.py --model "$M"
  echo "$M AgentIssue-Bench calibration exit $? $(date -Is)"
  echo "$M corrected-input reruns start $(date -Is)"
  "$PY" -u driver.py repair --model "$M" --corrected-input --reruns 5 --parallel 2
  echo "$M corrected-input reruns exit $? $(date -Is)"
  echo "$M AgentIssue-Bench tests start $(date -Is)"
  "$PY" -u test_repairs.py --models "$M"
  echo "$M AgentIssue-Bench tests exit $? $(date -Is)"
  "$PY" score_tests.py --models "$M" > "../score_$M.txt" 2>&1
  echo "$M AgentIssue-Bench score exit $? $(date -Is)"
}

agentdefect_calibration() {
  M="$1"
  cd "$AD"
  echo "$M AgentDefect calibration start $(date -Is)"
  "$PYAD" -u test_repairs.py --models "$M"
  echo "$M AgentDefect calibration exit $? $(date -Is)"
}

echo "queue start $(date -Is)"
wait_for "test_repairs.py --models gpt-oss-120b"
# resumes the gpt-oss-120b AgentDefect calibration if it stopped early, every finished record is skipped
agentdefect_calibration gpt-oss-120b
agentissue gpt-oss-120b
wait_for "run_arc_again.sh"
agentissue DeepSeek-V4.1-Flash
agentdefect_calibration DeepSeek-V4.1-Flash
wait_for "run_adapted.sh GLM-5.3"
agentissue GLM-5.3
agentdefect_calibration GLM-5.3
echo "queue end $(date -Is)"
