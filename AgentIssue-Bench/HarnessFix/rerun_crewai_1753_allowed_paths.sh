#!/bin/bash
# Plan step 3d: crewai_1753 again after the editable-paths fix of the AgentIssue-Bench mode, one rerun with
# gpt-oss-120b, detached from the Claude session. The step 3d rerun before the fix is in
# AgentIssue-Bench/HarnessFix/gpt-oss-120b/_pilot_3d_before_allowed_paths/.
cd /data/wang/junh/githubs/stochastic-harness
PY=/data/wang/junh/python/cpython-3.10.19/bin/python3.10
echo "agentissue start $(date +%H:%M:%S)"
$PY -u AgentIssue-Bench/HarnessFix/code/driver.py --model gpt-oss-120b --tags crewai_1753 --reruns 1
echo "agentissue exit $? $(date +%H:%M:%S)"
