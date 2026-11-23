#!/bin/bash
# Plan step 3d: rerun of the step 3c sample after the label, end note, leakage check and sandbox changes,
# five cases, one rerun each with gpt-oss-120b, one at a time. The step 3c reruns are in
# <dataset>/HarnessFix/gpt-oss-120b/_pilot_3c/.
cd /data/wang/junh/githubs/stochastic-harness
PY=/data/wang/junh/python/cpython-3.10.19/bin/python3.10
echo "agentdefect start $(date +%H:%M:%S)"
$PY -u AgentDefect/HarnessFix/code/driver.py --model gpt-oss-120b --cases 76379440 77099194 77921898 --reruns 1
echo "agentdefect exit $? $(date +%H:%M:%S)"
$PY -u AgentIssue-Bench/HarnessFix/code/driver.py --model gpt-oss-120b --tags sweagent_741 crewai_1753 --reruns 1
echo "agentissue exit $? $(date +%H:%M:%S)"
