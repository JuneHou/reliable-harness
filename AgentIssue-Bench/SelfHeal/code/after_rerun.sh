#!/bin/bash
# Fix plan departure 13: after the gpt-oss-120b calibration rerun ends (one test container at a time), run
# the corrected-evaluator controls its process could not see. ai_4411 and ai_5628 with the reinstall line
# dropped (Jun "2"), autogen_1844 and autogen_3361 with the reinstall line dropped (Jun "yes apply the same
# fix").
cd /data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/SelfHeal/code
while pgrep -f "calibrate.py --model gpt-oss-120b$" >/dev/null; do sleep 60; done
/data/wang/junh/envs/selfheal/bin/python calibrate.py --model gpt-oss-120b --tags ai_4411 ai_5628 autogen_1844 autogen_3361
