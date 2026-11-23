#!/bin/bash
# Plan step 3d, AgentIssue-Bench part, started again detached from the Claude session (setsid nohup) so it
# keeps running if the session ends. The first start of sweagent_741 was stopped after its relay was stopped,
# in its planning step, and is kept in AgentIssue-Bench/HarnessFix/gpt-oss-120b/_stopped_for_detach/.
cd /data/wang/junh/githubs/stochastic-harness
PY=/data/wang/junh/python/cpython-3.10.19/bin/python3.10
echo "agentissue start $(date +%H:%M:%S)"
$PY -u AgentIssue-Bench/HarnessFix/code/driver.py --model gpt-oss-120b --tags sweagent_741 crewai_1753 --reruns 1
echo "agentissue exit $? $(date +%H:%M:%S)"
