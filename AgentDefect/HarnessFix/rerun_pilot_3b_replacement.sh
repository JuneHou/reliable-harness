#!/bin/bash
# Plan step 3b: the one replacement of 77099194 rerun 1, whose first attempt stopped on a model call over
# HarnessFix's 300 s timeout (kept in 77099194/_replaced/rerun_1). Starts after rerun_pilot_3b.sh ends.
cd /data/wang/junh/githubs/stochastic-harness
while pgrep -f "rerun_pilot_3b.sh$|rerun_pilot_3b.sh " >/dev/null || pgrep -f "AgentIssue-Bench/HarnessFix/code/driver.py --model gpt-oss-120b" >/dev/null; do sleep 30; done
PY=/data/wang/junh/python/cpython-3.10.19/bin/python3.10
echo "replacement start $(date +%H:%M:%S)"
$PY -u AgentDefect/HarnessFix/code/driver.py --model gpt-oss-120b --cases 77099194 --reruns 1
echo "replacement exit $? $(date +%H:%M:%S)"
