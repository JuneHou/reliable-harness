#!/bin/bash
# Fix plan step 3 on AgentDefect: tests of the redone gpt-oss-120b and GLM-5.3 repairs, of every replaced first
# attempt, and the calibration of the 11 changed cases, one environment at a time (test_repairs.py).
#  1. pass 1 tests the environments whose reruns all have results, pass 2 the rest after GLM-5.3 ends
#  2. keep the first build's install records in test_env_logs/_first_build/
#  3. start Ollama on the CPU and pull the readmes' models (Jun "please fix the five cases")
#  4. run test_repairs.py over all lists
#  5. stop Ollama and delete Ollama, its models, tesseract and the Postgres image
#     (Jun "only one env at a time keep. all finish, all deleted")
# Usage: setsid nohup bash run_tests_fixplan.sh > ../run_tests_fixplan.log 2>&1 < /dev/null &
S=/data/wang/junh/githubs/stochastic-harness/AgentDefect/SelfHeal
T=/data/wang/junh/tools
PY=/data/wang/junh/python/cpython-3.10.19/bin/python3.10
cd $S
mkdir -p test_env_logs/_first_build && cp -n test_env_logs/*.json test_env_logs/*.log test_env_logs/_first_build/ 2>/dev/null
[ -f $T/tools_ready ] || { echo "tools not ready"; exit 1; }
export OLLAMA_HOST=127.0.0.1:11434 OLLAMA_MODELS=$T/ollama_models
CUDA_VISIBLE_DEVICES="" setsid nohup $T/ollama/bin/ollama serve > $T/ollama_serve.log 2>&1 < /dev/null &
sleep 10
for m in llama3 nomic-embed-text mxbai-embed-large mistral; do
  $T/ollama/bin/ollama pull $m >> $T/ollama_pull.log 2>&1 || { echo "ollama pull $m failed"; exit 1; }
done
echo "ollama models: $($T/ollama/bin/ollama list | tail -n +2 | awk '{print $1}' | tr '\n' ' ') $(date -Is)"
cd code
echo "pass 1, environments whose reruns all have results $(date -Is)"
$PY -u test_repairs.py
echo "pass 1 exit $? $(date -Is)"
echo "waiting for the GLM-5.3 replacements $(date -Is)"
while pgrep -f "driver.py repair --model GLM-5.3" > /dev/null; do sleep 60; done
echo "GLM-5.3 results $(ls ../GLM-5.3/[0-9h]*/rerun_*/Fix-Agent/results/*_result.txt | wc -l) of 185 $(date -Is)"
echo "pass 2, the deferred environments $(date -Is)"
$PY -u test_repairs.py
echo "exit $? $(date -Is)"
pkill -f "^$T/ollama/bin/ollama serve"
sleep 3
rm -rf $T/ollama $T/ollama_models $T/tesseract $T/tools_ready
docker rmi pgvector/pgvector:pg17
echo "tools deleted $(date -Is)"
