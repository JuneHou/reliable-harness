#!/bin/bash
# Wait until a rerun whose driver was stopped (run_agent.py PID) ends, then stop its relay (relay PID)
# and write driver_stopped.json in the rerun folder. Used for the two DeepSeek-V4.1-Flash reruns left
# running on OpenRouter when the run switched back to ARC (Jun "ok. let's switch back to arc").
# Usage: setsid nohup bash stop_relay_when_done.sh RUN_AGENT_PID RELAY_PID RERUN_DIR > /dev/null 2>&1 < /dev/null &
set -u
A="$1"; R="$2"; D="$3"
while kill -0 "$A" 2>/dev/null; do sleep 20; done
kill -TERM "$R" 2>/dev/null
cat > "$D/driver_stopped.json" <<EOF
{"note": "The OpenRouter driver was stopped while this rerun ran, so that the reruns not yet started run on ARC again (Jun \"ok. let's switch back to arc\"). This rerun ran on OpenRouter to its end under the stopped driver, its exit code was not captured, and the driver wrote no run_record.json for it. Its relay was stopped after run_agent.py ended.", "provider": "openrouter", "run_agent_ended": "$(date -Is)"}
EOF
