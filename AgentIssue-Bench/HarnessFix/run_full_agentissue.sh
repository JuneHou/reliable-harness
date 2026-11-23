#!/bin/bash
# Plan step 4, AgentIssue-Bench part: HarnessFix on all 50 issues, five reruns each, one rerun at a time, for one
# model. The driver pulls each issue's image, runs its reruns, and deletes the image it pulled (Jun "only one env
# at a time keep. all finish, all deleted"). A rerun whose final_record.json exists is kept, not run again.
#   bash AgentIssue-Bench/HarnessFix/run_full_agentissue.sh gpt-oss-120b
MODEL=${1:?model}
cd /data/wang/junh/githubs/stochastic-harness
PY=/data/wang/junh/python/cpython-3.10.19/bin/python3.10
# plan departure 7: AgentIssue-Bench may run beside AgentDefect, started on its own. The lock lets only one
# AgentIssue-Bench driver per model run, so the step 4 script's later AgentIssue-Bench part exits while the
# first one is still going, and never picks up the same unfinished rerun.
exec 9> "AgentIssue-Bench/HarnessFix/.driver_${MODEL}.lock"
if ! flock -n 9; then
  echo "agentissue for $MODEL already running elsewhere, this start exits $(date -Is)"
  exit 0
fi
echo "agentissue start $(date -Is)"
$PY -u AgentIssue-Bench/HarnessFix/code/driver.py --model "$MODEL"
echo "agentissue exit $? $(date -Is)"
