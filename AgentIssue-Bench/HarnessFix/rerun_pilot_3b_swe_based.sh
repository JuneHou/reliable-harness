#!/bin/bash
# Plan step 3b: sweagent_741 on the SWE-Bench-based AgentIssue-Bench mode, after the 77099194 replacement ends.
cd /data/wang/junh/githubs/stochastic-harness
while pgrep -f "rerun_pilot_3b_replacement.sh$|rerun_pilot_3b_replacement.sh " >/dev/null || pgrep -f "AgentDefect/HarnessFix/code/driver.py --model gpt-oss-120b" >/dev/null; do sleep 30; done
PY=/data/wang/junh/python/cpython-3.10.19/bin/python3.10
echo "start $(date +%H:%M:%S)"
$PY -u AgentIssue-Bench/HarnessFix/code/driver.py --model gpt-oss-120b --tags sweagent_741 --reruns 1
echo "agentissue exit $? $(date +%H:%M:%S)"
