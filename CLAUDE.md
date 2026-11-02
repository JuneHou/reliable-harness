# AgentDefect project rules

## Instruction fidelity

Execute exactly what the instruction says. Nothing enters the output that the instruction
does not name or clearly imply. The absence of a prohibition is not permission to add.

When Jun says "show X", show X and nothing else. Do not add context, summaries, tables,
or additional material not in the instruction — not even material that seems helpful or
relevant. Jun will ask for more if they want more.

Before doing any work: read the instruction back, word by word, and list everything it
asks for. Build only that list.

## Dataset example tabs

The dataset example tabs in the advisor artifact show only files the dataset authors
provided. This means:

- AgentDefect tab: only files in `motivation_pilot/artifacts/repairs/<case_id>/` that come
  from the SelfHeal archive — run_buggy.py, attempt_1.py, attempt_2.py for the chosen case.
- AgentIssue-Bench tab: only files the AgentIssue-Bench repository contains — repro JSON
  records in `inputs/agentissue/repro/` and generated patches in `Generated Patches/`.

Everything else is our experiment output and must not appear in these tabs. This includes
but is not limited to: comparisons.jsonl, reanalysis.jsonl, summary.json, boundary.json,
decision.json, configuration adequacy tables, enactment rate tables, PN tables, pilot
summaries, and any file produced by running our code.

## Artifact publish rule

Never publish an artifact update while a discussion is ongoing. Propose every change in
chat first. Publish only after Jun gives a written yes in that same discussion.

## No dates in documents

Never write dates in any report, artifact, or document — including prose, headers, meta
lines, callouts, and figure captions. File paths that contain dates as folder names (e.g.
`exp-2026-10-22/`) are source references and may remain.

## Forbidden words

Never use: "canon", "yardstick", "enact", "enactment". Use plain alternatives: for
enact/enactment use "execute" or "execution".

## No experiment except the motivation one in the artifact

The advisor artifact contains only the motivation pilot experiment. No other experiment
(surrogate audit, reanalysis, test1, boundary audit) appears in any tab of the artifact.
