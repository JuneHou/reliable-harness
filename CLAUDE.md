# stochastic-harness project rules

## Instruction fidelity

Execute exactly what the instruction says. Nothing enters the output that the instruction
does not name or clearly imply. The absence of a prohibition is not permission to add.

When Jun says "show X", show X and nothing else. Do not add context, summaries, tables,
or additional material not in the instruction — not even material that seems helpful or
relevant. Jun will ask for more if they want more.

Before doing any work: read the instruction back, word by word, and list everything it
asks for. Build only that list.

## Datasets

AgentDefect is the benchmark dataset at `/data/wang/junh/githubs/AgentDefect`. It is read-only
from this project. Do not write experiment output into that repository.

AgentIssue-Bench is the second dataset at `/data/wang/junh/githubs/AgentIssue-Bench`. Also
read-only from here.

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

## Number registry

Every number that appears in any document must have a row in `docs/NUMBERS.md` before it
is written. Run the number check after every edit to a document that contains numbers:

```
python3 ~/.claude/skills/number-check/scripts/check_numbers.py --registry docs/NUMBERS.md <file>
```
