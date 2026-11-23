#!/bin/bash
# Step 5 of SelfHeal's AgentDefect/SelfHeal/code/run_tests_fixplan.sh, after the six service cases: stop Ollama
# and delete Ollama, its models, tesseract and the Postgres image (Jun "only one env at a time keep. all finish,
# all deleted"). Kept when SelfHeal's own AgentDefect tests started in the meantime, so they are never cut off.
#   bash AgentDefect/HarnessFix/services_down.sh
T=/data/wang/junh/tools
SELFHEAL_TESTS="AgentDefect/SelfHeal/code/test_repairs.py|run_tests_fixplan.sh|test_original_and_repairs.py"
if pgrep -f "$SELFHEAL_TESTS" > /dev/null; then
  echo "SelfHeal's AgentDefect tests are running, services kept $(date -Is)"
  exit 0
fi
pkill -f "^$T/ollama/bin/ollama serve"
sleep 3
rm -rf $T/ollama $T/ollama_models $T/tesseract $T/tools_ready
docker rmi pgvector/pgvector:pg17
echo "services deleted $(date -Is)"
