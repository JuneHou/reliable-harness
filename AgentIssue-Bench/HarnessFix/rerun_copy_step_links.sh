#!/bin/bash
# Plan departure 8 (Jun "yes", 2026-11-19): after HarnessFix's agentissue copy step keeps links as links, each rerun
# of ai_5628 and ai_6510 that stopped at that copy gets its one replacement. The stopped reruns are kept in
# AgentIssue-Bench/HarnessFix/<model>/_stopped_at_copy_step/. This script waits until no AgentIssue-Bench driver of the
# model holds the lock, then starts run_full_agentissue.sh once more; the driver runs only reruns with no
# final_record.json, which are these eight. If another start takes the lock first, it waits again.
#   setsid -f nohup bash AgentIssue-Bench/HarnessFix/rerun_copy_step_links.sh gpt-oss-120b >> step4_harnessfix_gpt-oss-120b_agentissue.log 2>&1 < /dev/null
MODEL=${1:?model}
cd /data/wang/junh/githubs/stochastic-harness
LOCK="AgentIssue-Bench/HarnessFix/.driver_${MODEL}.lock"
RERUNS="ai_5628/rerun_3 ai_5628/rerun_4 ai_5628/rerun_5 ai_6510/rerun_1 ai_6510/rerun_2 ai_6510/rerun_3 ai_6510/rerun_4 ai_6510/rerun_5"
missing() {
  n=0
  for r in $RERUNS; do [ -f "AgentIssue-Bench/HarnessFix/$MODEL/$r/final_record.json" ] || n=$((n+1)); done
  echo $n
}
echo "copy step replacements for $MODEL waiting $(date -Is), missing $(missing)"
while [ "$(missing)" -gt 0 ]; do
  if flock -n "$LOCK" true; then
    # the driver's lines reach the log as they are printed, and a copy is kept to see whether this start ran
    OUT="AgentIssue-Bench/HarnessFix/.copy_step_start_${MODEL}.out"
    bash AgentIssue-Bench/HarnessFix/run_full_agentissue.sh "$MODEL" 2>&1 | tee "$OUT"
    if ! grep -q "already running elsewhere" "$OUT"; then
      echo "copy step replacements for $MODEL done $(date -Is), missing $(missing)"
      exit 0
    fi
  fi
  sleep 300
done
echo "copy step replacements for $MODEL nothing missing $(date -Is)"
