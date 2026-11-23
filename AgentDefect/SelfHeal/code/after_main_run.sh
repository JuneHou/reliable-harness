#!/bin/bash
# After the main test run ends:
#  1. clean the finished tests the main run's process left uncleaned
#  2. start Ollama on the CPU and pull the readmes' models, once the tools are installed
#  3. delete the tests of seven cases and run them again in lists 1, 2 and 11:
#     78366661, 78235199 (test.py imports the repair, Jun "tested with their test.py importing the repair")
#     78429932, 78838421, 79497660, 77555312, 78188862 (Jun "please fix the five cases")
#  4. stop Ollama, delete Ollama, its models, tesseract and the Postgres image
#     (Jun "ollama will be deleted after the run finished")
S=/data/wang/junh/githubs/stochastic-harness/AgentDefect/SelfHeal
T=/data/wang/junh/tools
PY=/data/wang/junh/python/cpython-3.10.19/bin/python3.10
LOG=$S/test_repairs_run_fixes.log
cd $S
until grep -q "^exit [0-9]*$" test_repairs_run.log; do sleep 60; done
$PY - <<'PYEOF' >> $LOG 2>&1
import sys, os, glob
sys.path.insert(0, "code"); import test_repairs as t
n = total = 0
for f in glob.glob("*/*/rerun_*/test/test_record.json"):
    d = os.path.dirname(f); total += t.clean_test(d, d.split("/")[1]); n += 1
print("cleaned", n, "finished tests, removed", round(total / 1e9, 1), "GB", flush=True)
PYEOF
rm -rf /data/wang/junh/.cache/llama_index/models
echo "waiting for the tools (setup_tools2.sh writes $T/tools_ready)" >> $LOG
until [ -f $T/tools_ready ]; do sleep 60; done
export OLLAMA_HOST=127.0.0.1:11434 OLLAMA_MODELS=$T/ollama_models
CUDA_VISIBLE_DEVICES="" setsid nohup $T/ollama/bin/ollama serve > $T/ollama_serve.log 2>&1 < /dev/null &
sleep 10
for m in llama3 nomic-embed-text mxbai-embed-large mistral; do
  $T/ollama/bin/ollama pull $m >> $T/ollama_pull.log 2>&1 || { echo "ollama pull $m failed" >> $LOG; exit 1; }
done
echo "ollama models: $($T/ollama/bin/ollama list | tail -n +2 | awk '{print $1}' | tr '\n' ' ')" >> $LOG
for c in 78366661 78235199 78429932 78838421 79497660 77555312 78188862; do rm -rf */$c/rerun_*/test; done
cd code && $PY -u test_repairs.py --lists 1 2 11 >> $LOG 2>&1
echo "exit $?" >> $LOG
pkill -f "^$T/ollama/bin/ollama serve"
sleep 3
rm -rf $T/ollama $T/ollama_models $T/tesseract
docker rmi pgvector/pgvector:pg17 >> $LOG 2>&1
echo "tools deleted: $(ls $T 2>/dev/null | tr '\n' ' ')" >> $LOG
