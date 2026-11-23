#!/bin/bash
# Streaming redo of gpt-oss-120b and GLM-5.3 on AgentDefect (fix plan, departure 1, Jun "gpt-oss and GLM, full").
# Their earlier work, run before the relay streamed, is in <model>/_not_streamed/. For each model in turn:
# the rules and intents and the 185 reruns by run_model.sh, then reruns whose search failed or that
# stopped are moved aside once and run once more, so each planned repetition gets at most one
# replacement (Jun "allow at most one replacement per original planned repetition").
# Usage: setsid nohup bash redo_streaming.sh > ../redo_streaming.log 2>&1 < /dev/null &
set -u
cd /data/wang/junh/githubs/stochastic-harness/AgentDefect/SelfHeal/code
PY=/data/wang/junh/envs/selfheal/bin/python
for M in gpt-oss-120b GLM-5.3; do
  echo "model start $M $(date -Is)"
  bash run_model.sh "$M" >> "../run_$M.log" 2>&1
  echo "run_model exit $? $M $(date -Is)"
  {
    echo "move aside start $M $(date -Is)"
    "$PY" move_aside.py "$M"
    echo "replacement start $M $(date -Is)"
    "$PY" driver.py repair --model "$M" --reruns 5 --parallel 5
    echo "replacement exit $? $(date -Is)"
    "$PY" move_aside.py "$M" --check
  } >> "../run_$M.log" 2>&1
  echo "model done $M $(date -Is)"
done
