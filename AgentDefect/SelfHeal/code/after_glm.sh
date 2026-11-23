#!/bin/bash
# Run the remaining SelfHeal repairs one model at a time, because two models searching DuckDuckGo
# at once made the searches time out. After the GLM-5.3 repairs end, redo its reruns whose search
# failed. Then move the DeepSeek-V4.1-Flash reruns whose search failed or that were stopped, and
# run its repairs. Each model's lines go to its own run log.
# Usage: setsid nohup bash after_glm.sh > ../after_glm.log 2>&1 < /dev/null &
set -u
cd /data/wang/junh/githubs/stochastic-harness/AgentDefect/SelfHeal/code
PY=/data/wang/junh/envs/selfheal/bin/python
echo "waiting for the GLM-5.3 run $(date -Is)"
while pgrep -f "[r]un_model.sh GLM-5.3" > /dev/null; do sleep 60; done
for M in GLM-5.3 DeepSeek-V4.1-Flash; do
  {
    echo "move aside start $M $(date -Is)"
    "$PY" move_aside.py "$M"
    echo "repair start $M $(date -Is)"
    "$PY" driver.py repair --model "$M" --reruns 5 --parallel 5
    echo "repair exit $? $(date -Is)"
    "$PY" move_aside.py "$M" --check
  } >> "../run_$M.log" 2>&1
  echo "done $M $(date -Is)"
done
