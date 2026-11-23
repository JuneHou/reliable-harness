#!/bin/bash
# Resume one model's AgentIssue-Bench run after an ARC outage stopped its file picking.
# A pick whose model call failed writes no pick.json, only pick_errors.json, so the pick step tries it
# again. The pick step runs every ten minutes, at most 12 times, until every issue whose report names no
# file has its pick.json. Only then does run_adapted.sh start the repair loop and the redo, reusing the
# finished rules and intents. If the picks are still incomplete after 12 tries, nothing more runs.
# Usage: setsid nohup bash resume_after_outage.sh DeepSeek-V4.1-Flash >> ../run_DeepSeek-V4.1-Flash.log 2>&1 < /dev/null &
set -u
M="$1"
cd /data/wang/junh/githubs/stochastic-harness/AgentIssue-Bench/SelfHeal/code
PY=/data/wang/junh/envs/selfheal/bin/python
NEED=$("$PY" -I -c "import json;print(sum(1 for v in json.load(open('../inputs/named_files.json')).values() if not v))")
for try in $(seq 1 12); do
  sleep 600
  echo "pick try $try $M $(date -Is)"
  "$PY" driver.py pick --model "$M"
  HAVE=$(ls ../$M/*/pick/pick.json 2>/dev/null | wc -l)
  echo "picks $HAVE of $NEED $(date -Is)"
  if [ "$HAVE" -ge "$NEED" ]; then
    echo "all picks done, starting run_adapted.sh $(date -Is)"
    exec bash run_adapted.sh "$M"
  fi
done
echo "picks incomplete after 12 tries, nothing more run $(date -Is)"
exit 1
