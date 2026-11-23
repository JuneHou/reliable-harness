#!/bin/bash
# Plan step 3b: rerun of the pilot sample after the specification and acceptance check items, one rerun at a time.
cd /data/wang/junh/githubs/stochastic-harness
PY=/data/wang/junh/python/cpython-3.10.19/bin/python3.10
echo "start $(date +%H:%M:%S)"
$PY -u AgentDefect/HarnessFix/code/driver.py --model gpt-oss-120b --cases 76379440 77099194 --reruns 1
echo "agentdefect exit $? $(date +%H:%M:%S)"
$PY -u AgentIssue-Bench/HarnessFix/code/driver.py --model gpt-oss-120b --tags sweagent_741 --reruns 1
echo "agentissue exit $? $(date +%H:%M:%S)"
