#!/bin/bash
# Plan "why SelfHeal fails on AgentIssue-Bench's multi-file issues", step 3. after_plan_audit.sh keeps running
# unchanged and gives DeepSeek-V4.1-Flash the same calibration, reruns and tests as gpt-oss-120b. This job waits
# until that queue logs DeepSeek-V4.1-Flash's score, then scores both models together and runs the analysis.
# Nothing waits for GLM-5.3 (Jun "don't need wait for GLM 5.3 but wait for deep seek").
# Usage: setsid nohup bash after_deepseek_analysis.sh > ../after_deepseek_analysis.log 2>&1 < /dev/null &
set -u
cd /data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/SelfHeal/code
PY=/data/wang/junh/envs/selfheal/bin/python
echo "waiting for DeepSeek-V4.1-Flash's score in after_plan_audit.log $(date -Is)"
until grep -q "DeepSeek-V4.1-Flash AgentIssue-Bench score exit" ../after_plan_audit.log; do sleep 300; done
echo "DeepSeek-V4.1-Flash scored $(date -Is)"
"$PY" score_tests.py --models gpt-oss-120b DeepSeek-V4.1-Flash > ../score_gpt-oss-120b_DeepSeek-V4.1-Flash.txt 2>&1
echo "score of both models exit $? $(date -Is)"
"$PY" analyze_multifile.py --models gpt-oss-120b DeepSeek-V4.1-Flash > ../multifile_analysis.txt 2>&1
echo "analysis exit $? $(date -Is)"
