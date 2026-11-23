#!/bin/bash
# Plan step 4: HarnessFix full runs for one model, AgentDefect first, then AgentIssue-Bench, never both at once.
# Started detached: setsid -f nohup bash run_step4_harnessfix.sh gpt-oss-120b > step4_harnessfix_<model>.log 2>&1 < /dev/null
MODEL=${1:?model}
cd /data/wang/junh/githubs/stochastic-harness
echo "step 4 $MODEL start $(date -Is)"
bash AgentDefect/HarnessFix/run_full_agentdefect.sh "$MODEL"
echo "agentdefect part ended $(date -Is)"
bash AgentIssue-Bench/HarnessFix/run_full_agentissue.sh "$MODEL"
echo "step 4 $MODEL end $(date -Is)"
