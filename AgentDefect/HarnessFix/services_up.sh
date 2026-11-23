#!/bin/bash
# Plan decision "services for six AgentDefect cases": Ollama, tesseract and the Postgres image with pgvector, set
# up again from /data/wang/junh/tools before the cases that need them, as SelfHeal's own test script does
# (AgentDefect/SelfHeal/code/run_tests_fixplan.sh, steps 3 and 4). SelfHeal's run_test then uses them
# unchanged: it checks Ollama's models (ollama_ready), starts a Postgres container per test (start_postgres)
# and puts tesseract on the program's PATH. services_down.sh deletes them afterwards.
#   bash AgentDefect/HarnessFix/services_up.sh
set -e
T=/data/wang/junh/tools
SH=/data/wang/junh/githubs/stochastic-harness
PY=/data/wang/junh/python/cpython-3.10.19/bin/python3.10
SELFHEAL_TESTS="AgentDefect/SelfHeal/code/test_repairs.py|run_tests_fixplan.sh|test_original_and_repairs.py"
# never set up or take over the services while SelfHeal's own AgentDefect tests use them
while pgrep -f "$SELFHEAL_TESTS" > /dev/null; do echo "waiting for SelfHeal's AgentDefect tests $(date -Is)"; sleep 60; done
[ -x $T/ollama/bin/ollama ] || bash $T/setup_ollama.sh
[ -f $T/tools_ready ] || bash $T/setup_tools2.sh
export OLLAMA_HOST=127.0.0.1:11434 OLLAMA_MODELS=$T/ollama_models
if ! pgrep -f "^$T/ollama/bin/ollama serve" > /dev/null; then
  CUDA_VISIBLE_DEVICES="" setsid nohup $T/ollama/bin/ollama serve > $T/ollama_serve.log 2>&1 < /dev/null &
  sleep 10
fi
# the models SelfHeal's test path checks for, read from its own table (test_repairs.py OLLAMA_CASES)
MODELS=$($PY -c "import sys; sys.path.insert(0, '$SH/AgentDefect/SelfHeal/code'); import test_repairs as t; print(' '.join(sorted({m for v in t.OLLAMA_CASES.values() for m in v})))")
for m in $MODELS; do
  $T/ollama/bin/ollama pull $m >> $T/ollama_pull.log 2>&1 || { echo "ollama pull $m failed"; exit 1; }
done
$PY -c "
import sys; sys.path.insert(0, '$SH/AgentDefect/SelfHeal/code'); import test_repairs as t
for case, models in t.OLLAMA_CASES.items():
    print('ollama ready for', case, t.ollama_ready(models))"
echo "tesseract: $($T/tesseract/bin/tesseract --version 2>&1 | head -1)"
echo "postgres image: $(docker image inspect pgvector/pgvector:pg17 --format '{{.Id}}')"
echo "services up $(date -Is)"
