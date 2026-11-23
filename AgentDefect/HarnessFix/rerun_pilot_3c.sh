#!/bin/bash
# Plan step 3c: the step 3b sample (AgentDefect 76379440 and 77099194, AgentIssue-Bench sweagent_741) and the
# two cases of departure 6 (AgentDefect 77921898, AgentIssue-Bench crewai_1753), one rerun each with gpt-oss-120b,
# one at a time, after the run record, diagnosis file list and bash changes. The step 3b reruns are in
# <dataset>/HarnessFix/gpt-oss-120b/_pilot_3b/.
cd /data/wang/junh/githubs/stochastic-harness
PY=/data/wang/junh/python/cpython-3.10.19/bin/python3.10
echo "agentdefect start $(date +%H:%M:%S)"
$PY -u AgentDefect/HarnessFix/code/driver.py --model gpt-oss-120b --cases 76379440 77099194 77921898 --reruns 1
echo "agentdefect exit $? $(date +%H:%M:%S)"
$PY -u AgentIssue-Bench/HarnessFix/code/driver.py --model gpt-oss-120b --tags sweagent_741 crewai_1753 --reruns 1
echo "agentissue exit $? $(date +%H:%M:%S)"
