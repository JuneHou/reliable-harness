# motivation_pilot

The AgentDefect motivation pilot and its extension exp-2026-10-22, which asks which persistent component changes of the existing complete repairs are required, removable or dependent, and whether measuring that changes the repair we would keep.

The plan is `~/.claude/plans/back-to-agent-defect-deep-blossom.md`. Jun's instructions are copied verbatim in `artifacts/agentdefect_extension/exp-2026-10-22/instruction_2026-10-22.md`.

## Commands

Run every command from this folder with the study interpreter.

```bash
cd /data/wang/junh/githubs/AgentDefect/motivation_pilot
PY=/data/wang/junh/envs/harnessfix/bin/python

# offline tests, no key and no network
$PY -m pytest tests -q

# offline preparation
PYTHONPATH=src $PY -m motivation_pilot.extension map
PYTHONPATH=src $PY -m motivation_pilot.extension manifest
PYTHONPATH=src $PY -m motivation_pilot.extension selftest

# live stage, needs OPENAI_API_KEY; the same command resumes after an interruption
PYTHONPATH=src nohup $PY -m motivation_pilot.extension live > artifacts/agentdefect_extension/exp-2026-10-22/live.log 2>&1 &

# recompute comparisons, decisions and the report from the recorded runs
PYTHONPATH=src $PY -m motivation_pilot.extension compare
PYTHONPATH=src $PY -m motivation_pilot.extension report

# 78383658 retrieval intervention R, experiment exp-2026-10-22-r (report section 7)
PYTHONPATH=src $PY -m motivation_pilot.retrieval_extension manifest
PYTHONPATH=src $PY -m motivation_pilot.retrieval_extension selftest
PYTHONPATH=src nohup $PY -m motivation_pilot.retrieval_extension live > artifacts/agentdefect_extension/exp-2026-10-22-r/live.log 2>&1 &
PYTHONPATH=src $PY -m motivation_pilot.retrieval_extension compare

# environment flip experiment exp-2026-10-23-e (report section 8); the 79343179 E1 runs use /data/wang/junh/envs/harnessfix-pandas2
PYTHONPATH=src $PY -m motivation_pilot.environment_extension manifest
PYTHONPATH=src $PY -m motivation_pilot.environment_extension selftest
cd /data/wang/junh/githubs/AgentDefect/motivation_pilot && PYTHONPATH=src nohup /data/wang/junh/envs/harnessfix/bin/python -m motivation_pilot.environment_extension live > /data/wang/junh/githubs/AgentDefect/motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-e/live.log 2>&1 &
PYTHONPATH=src $PY -m motivation_pilot.environment_extension compare

# verdict reanalysis exp-2026-10-23-v (report section 9), no model call; add --delta 0.1 for the stricter margin
PYTHONPATH=src $PY -m motivation_pilot.verdict_reanalysis run
PYTHONPATH=src $PY -m motivation_pilot.extension report
```

A run has finished when `ps aux | grep extension | grep live` prints nothing and the last line of its `live.log` begins with `decision` or names the report files.

`live` exits with 2 when `configs/study.yaml` differs from the prelude settings, 3 when probes change the 76906469 outcomes, 4 when a recorded run's fingerprint no longer matches, 5 when the self test is missing or older than `instrument.py`, 6 without `OPENAI_API_KEY`, and 7 without the manifest. The retrieval and environment experiments use the same codes except 3, since every one of their cells is probed.

## File map

| path | content |
|---|---|
| `src/motivation_pilot/pilot_run.py` | the 2026-10-20 pilot runner; `_run_module` also serves the extension with one attempt and probes |
| `src/motivation_pilot/instrument.py` | child prelude, probes on resolved concrete classes, trace reader, derived fields |
| `src/motivation_pilot/extension.py` | configurations, decomposition and coherence checks, qualification, live runner, comparisons, decisions, report |
| `src/motivation_pilot/retrieval_extension.py` | the 78383658 retrieval intervention R, exp-2026-10-22-r |
| `artifacts/agentdefect_extension/exp-2026-10-22-r/` | its manifest, predictions, runs, traces, comparisons and decision |
| `src/motivation_pilot/environment_extension.py` | the environment flip experiment exp-2026-10-23-e, with its own runner `run_cell` |
| `artifacts/agentdefect_extension/exp-2026-10-23-e/` | its instruction, manifest, case files with `environment.json` and `control_96.csv`, predictions, runs, traces, comparisons, `flips.jsonl`, decisions and `summary.json` |
| `src/motivation_pilot/verdict_stats.py` | the estimator of the verdict reanalysis, Jeffreys posteriors, the contrast, PN and PS, Fisher's exact p |
| `src/motivation_pilot/verdict_reanalysis.py` | the verdict reanalysis exp-2026-10-23-v over every recorded comparison |
| `artifacts/agentdefect_extension/exp-2026-10-23-v/` | its instruction, `reanalysis.jsonl`, `enactment.jsonl`, `cells.jsonl` and `summary.json` |
| `tests/test_pipeline.py`, `tests/test_extension.py` | offline tests |
| `artifacts/frozen_oracles.json` | the frozen checks of the pilot, unchanged |
| `artifacts/frozen_oracles_v2.json`, `artifacts/oracle_corrections.json` | the versioned 77178370 correction and its log |
| `artifacts/agentdefect_extension/exp-2026-10-22/cases/<id>/` | contract, components, actions, configurations, decomposition and probe specification per case |
| `artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl`, `traces/` | one record per run and its event trace |
| `artifacts/agentdefect_extension/exp-2026-10-22/comparisons.jsonl`, `contribution_verdicts.csv`, `decisions.jsonl` | derived results |
| `artifacts/agentdefect_extension/exp-2026-10-22/report.md`, `limitations.md` | the report |
| `NUMBERS.md` | number registry, `ext_` rows between the `ext` markers |
