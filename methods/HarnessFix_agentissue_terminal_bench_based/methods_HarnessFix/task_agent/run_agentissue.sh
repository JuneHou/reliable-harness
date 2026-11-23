#!/usr/bin/env bash
# stochastic-harness adapter: runs the case's program with its test for HarnessFix, in the
# Terminal-Bench trace layout. Same arguments as run_terminal_bench.sh.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="${AGENT_SRC_DIR:-$SCRIPT_DIR/agentissue_program}"
exec "${HF_CASE_PYTHON:?set by the stochastic-harness driver}" "${HF_EXEC_CASE:?set by the stochastic-harness driver}" --agent-src "$SRC" "$@"
