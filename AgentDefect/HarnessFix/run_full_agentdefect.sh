#!/bin/bash
# Plan step 4, AgentDefect part: HarnessFix on all 37 cases, five reruns each, one rerun at a time, for one model.
# The cases that need no service run first. Then services_up.sh sets up Ollama, tesseract and the Postgres image,
# the cases that need them run, and services_down.sh deletes the services (plan decision "services for six
# AgentDefect cases"). The service cases are read from SelfHeal's own test table, so the two never differ.
#   bash AgentDefect/HarnessFix/run_full_agentdefect.sh gpt-oss-120b
set -e
MODEL=${1:?model}
cd /data/wang/junh/githubs/stochastic-harness
PY=/data/wang/junh/python/cpython-3.10.19/bin/python3.10
SERVICE=$($PY -c "import sys; sys.path.insert(0, 'AgentDefect/SelfHeal/code'); import test_repairs as t; print(' '.join(sorted(set(t.OLLAMA_CASES) | {t.PG_CASE, t.TESSERACT_CASE})))")
PLAIN=$(ls AgentDefect/HarnessFix/inputs/programs | grep -v -x -F -f <(echo "$SERVICE" | tr ' ' '\n') | tr '\n' ' ')
echo "service cases: $SERVICE"
echo "other cases: $(echo $PLAIN | wc -w)"
echo "cases without services start $(date -Is)"
$PY -u AgentDefect/HarnessFix/code/driver.py --model "$MODEL" --cases $PLAIN
bash AgentDefect/HarnessFix/services_up.sh
echo "service cases start $(date -Is)"
set +e
$PY -u AgentDefect/HarnessFix/code/driver.py --model "$MODEL" --cases $SERVICE
rc=$?
bash AgentDefect/HarnessFix/services_down.sh
echo "agentdefect exit $rc $(date -Is)"
