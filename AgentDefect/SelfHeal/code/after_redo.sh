#!/bin/bash
# After after_glm.sh ends, redo once more each model's reruns whose search failed during the
# first redo, one model at a time and two reruns at once, because DeepSeek-V4.1-Flash on ARC
# fails under heavier load. Each model's lines go to its own run log.
# Usage: setsid nohup bash after_redo.sh > ../after_redo.log 2>&1 < /dev/null &
set -u
cd /data/wang/junh/githubs/stochastic-harness/AgentDefect/SelfHeal/code
PY=/data/wang/junh/envs/selfheal/bin/python
echo "waiting for after_glm.sh $(date -Is)"
while pgrep -f "[a]fter_glm.sh" > /dev/null; do sleep 60; done
for M in GLM-5.3 DeepSeek-V4.1-Flash; do
  {
    echo "move aside start $M $(date -Is)"
    "$PY" move_aside.py "$M"
    echo "repair start $M $(date -Is)"
    "$PY" driver.py repair --model "$M" --reruns 5 --parallel 2
    echo "repair exit $? $(date -Is)"
    "$PY" move_aside.py "$M" --check
  } >> "../run_$M.log" 2>&1
  echo "done $M $(date -Is)"
done
