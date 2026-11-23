#!/bin/bash
# Plan step 3b: the one replacement of sweagent_741 rerun 1 on the SWE-Bench-based mode, with the 900 s limit
# per model call (departure 3). The first attempt stopped on a reply over 300 s and is kept in sweagent_741/_replaced/rerun_1.
cd /data/wang/junh/githubs/stochastic-harness
PY=/data/wang/junh/python/cpython-3.10.19/bin/python3.10
echo "start $(date +%H:%M:%S)"
$PY -u AgentIssue-Bench/HarnessFix/code/driver.py --model gpt-oss-120b --tags sweagent_741 --reruns 1
echo "agentissue exit $? $(date +%H:%M:%S)"
