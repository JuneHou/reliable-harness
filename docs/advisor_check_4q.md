# Advisor check: 4 questions on harness repair papers

Source: `docs/Agent_Error_Mitigation_Review (1).html`, 21 harness papers in section 5.
Data: `motivation_pilot/artifacts/agentdefect_extension/`.

---

## Combined table — 21 harness papers on 4 dimensions

Updated 2026-11-01 (Harness² and ModularRSI Q3 labels corrected to yes, Jun 2026-11-01). Q3 is reframed as: does repair validation establish that the specific repair executed? This is separate from whether the repair is causally necessary; that question is addressed in the Q3 section. Q2 now records what evidence is actually used, not only whether outcome is final-only.

| paper | Q1 — how proposed or judged | Q2 — error/evaluation evidence | Q3 — repair execution confirmed? | repair validation gate | Q4 — success criteria |
|---|---|---|---|---|---|
| HarnessFix | Four LLM roles: trace abstractor, diagnoser, patch generator, validation agent | state effects, data/control flow, source anchors, task outcomes | no — acceptance gate checks specification compliance, not per-mechanism activation | static check + validation-task execution with target-improvement and regression limit | task pass rate ↑ on GAIA/SWE/AppWorld/TB; regression limit on validation tasks |
| CHILL-Harness | Learned CIEL predicts intervention preferences; ARCO generates and authorizes workflow alternatives | intermediate checkpoints: memory, tool/env state; offline paired factual/alternative outcomes | partial — logs orchestration-decision routes, fallbacks, and authorizations; individual edit activation not required | offline paired execution trains effect estimates; online authorization uses predicted advantage | task success, total tokens, tokens per solved task, end-to-end runtime |
| Harness-R1 | Dedicated engineer trained through SFT then GRPO on executed patch utility | task constraints, action/observation excerpts, outcomes, environment state | partial — no-intervention/inert-patch reward is zero; per-conditional-branch coverage not established | same-batch rerun: patched-minus-baseline reward; invalid and inert patches receive zero reward | task pass rate on WebShop, ALFWorld, DBBench; shaped score; cross-benchmark average |
| HarnessCompass | LLM evolves structural and guidance tracks; R3 recombines and removes redundant edits | trajectories, verifier outcomes, first-person feedback grounded in traces | no — selection rule does not require per-edit activation finding for retained changes | evaluate both tracks on 50-task evolution set; integrate compatible edits; 450 disjoint tasks are final evaluation | Pass@1 on evolution, held-out, and full sets; cross-model transfer |
| JIT-Agent | SFT/DPO on teacher harnesses; Evo-GDPO online; execution feedback derives preference pairs | compiler errors, interface mismatches, tool-call failures, runtime exceptions, reward/latency/cost feedback | partial — invoked modules execute through protocol; conditional logic inside invoked modules can remain unexercised | protocol validation + up to two repair rounds; bank retention uses reward/latency/cost frontier | task accuracy, F1, rubric scores, latency, and monetary cost (reported separately) |
| ActiveSaddler | Bandit selects scenarios; underlying harness optimizer generates and evaluates edits | failure diagnoses from execution records become recurring-pattern arms | case study — one confirmed case of hook non-triggering; not a demonstrated universal gate | development data support candidate selection; regression checks; final test tasks separate | Test Pass@1, mean ± SD over three test-time executions |
| RePAIR | Local revert ranked by paired-t interval (full methods inaccessible) | patch-level history; paired outcome differences re-estimated after each accepted rollback | no — paired evaluation does not establish that both arms exercised the edited mechanism | resettable paired evaluation; stale evidence discarded when patch state changes | rollback-direction accuracy; Salvage Rate and Salvage Gain at patch level |
| Self-Harness | Fixed model proposes bounded edits from verifier-grounded failure clusters | terminal verifier reasoning, agent behavior, mechanism evidence in traces | no — split-level promotion outcomes; representative trace analysis does not gate per-edit activation | evaluate on held-in and held-out splits, normally two attempts; accepts nonneg on both, strict gain on at least one | mean single-attempt pass rate by split |
| Meta-Harness | LLM coding proposer searches harness code with history of candidates and scores | source code, scores, prompts, tool calls, model outputs, state updates | no — traces inspectable but loop does not require per-edit activation finding | interface validation + execution on search set; Pareto frontier; final test feedback withheld from proposer | domain task performance; context/token cost; Pareto trade-offs |
| RRSI | LLM proposes edits under annealed edit budget; a critic screens diffs for leakage and inertness | trajectory feedback; per-candidate hypothesis, diff, score/cost, and acceptance records | no — static inertness screening exists; runtime conditional-branch activation not checked | critic rejects leakage and inert edits; score floor (best observed minus noise band) plus complexity/cost rules | task score and policy-token cost; held-out/transfer; paired task-bootstrap intervals |
| ModularRSI | Code-Modify Agent analyzes trajectories, ranks function changes by task votes, edits modules independently | same-task successful/failed trajectories, binary rewards, function-level evidence | yes — on sampled tasks: gates on execution of two sampled tasks with rollback on failure; those tasks may bypass the modified function on other inputs | static check → diff review → execution on two sampled tasks; failed gates roll back | Acc, Pass@3, Pass³ (all-three success), StepNum (mean interaction steps) |
| Harness² | LLM proposes; composer requires a trajectory moment showing the edit's mechanism; selector chooses | matched candidate/reference trajectories, deliverables, diffs, task materials | yes — qualitative: composer requires a concrete trajectory moment demonstrating the retained edit's mechanism; not instrumented branch coverage | executes candidate probes on same task; composes from behavioral evidence; then executes successor | external benchmark check fractions; weighted rubric and judge-based scores; execution/improvement cost |
| SelfHeal | Fix ReAct agent proposes; a separate LLM critic checks code, API usage, and format | buggy code, intended behavior, test code, fix rules, API documentation | no — no code execution during debug loop; subsequent test success does not establish changed-path execution | up to three fix–critic iterations; returns last code even if final critic rejects | repair resolution rate; localization accuracy; attempts, time, and cost |
| GEPA | LLM reflects on module traces and mutates prompt; Pareto selection chooses parents | execution traces plus textual evaluator feedback (compiler output, etc.) | partial — changed prompt is received when its module is invoked; conditional module skipping and instruction compliance are not verified | execute before/after candidates on minibatch; broader Pareto evaluation on improvement | task scores across reasoning, QA, verification; rollout/sample efficiency |
| ACE | LLM generator, LLM reflector, curator writes context deltas | execution feedback; generator reports on helpful/harmful playbook entries | no — helpful/harmful entry counters are self-reported; actual instruction enactment not independently verified | offline adaptation precedes test; online mode predicts first then updates context for subsequent samples | AppWorld TGC/SGC; domain accuracy and judge-based evaluation; adaptation/inference cost |
| ADAS | Meta agent writes executable agent programs; two novelty/self-reflection steps | archive designs, evaluation metrics, execution errors | no — executability checked; newly added conditional mechanisms need not activate on validation tasks | runs programs on validation data, archives with metrics; execution errors trigger up to five revisions | task success/accuracy; reading-comprehension F1; transfer across tasks and models |
| AFlow | LLM edits workflow code, prompts, and connections within Monte Carlo tree search | tree-structured edit history, improvements/failures, prediction-vs-expected logs | no — five executions per candidate establish outcome evidence; modified conditional node reach not guaranteed | five executions on validation set; mean/SD feed search and recorded experience | math solve rate; coding Pass@1; QA F1; token-derived cost/performance |
| DGM | LLM coding agent edits own source from benchmark evaluation logs | benchmark evaluation logs and agent behavior | no — executability and self-editing capability checked; per-mechanism activation not established | evaluates descendants on coding benchmarks; archive requires compilation and retained self-editing | SWE-bench and Polyglot performance; archive/search progression |
| FlowFixer | Symbolic constraint inference localizes; LLM generates edits; LLM assesses semantics and relevance | node outputs vs. inferred specifications, violation rates, downstream influence, workflow traces | no — four pre-execution assessments are acceptance stages; successful rerun can bypass a changed conditional node | four pre-execution checks + dynamic verification on original inputs | Repair Success Rate, Failure Attribution Accuracy, Root Cause Accuracy; three-run average |
| CHASE | Proposer edits harness; Challenger generates protocol transformations; confirmation gates archive | harness scores/traces; gain destruction under counterfactual protocols; semantic-validity evidence | no — checks robustness to protocol shortcuts; individual repair-mechanism activation not verified | executes candidates and transformed benchmarks; validity + confirmation admits to archive | released-benchmark score; counterfactual gain destruction; archived-protocol scores; token use |
| DARC | Development-trace diagnosis restricts a fixed recovery library; verifier selects a frozen policy | invalid/state-incompatible actions, missing procedures, format violations, intervention outcomes | yes at invocation level — distinguishes invoked recovery from not-attempted; internal branches are finer granularity | evaluates intervention attempts under controlled protocols; resets apply where available | ALFWorld success; AppWorld TGC/SGC; Finance accuracy; environment steps/retrieval budget; bootstrap intervals |

---

## Q1 — How repair patches are proposed and judged

Patch generation and patch judgment are two separate roles in these papers. Most papers use a prompted LLM to generate the patch. A separate LLM evaluative role exists in several: SelfHeal has an independent critic that issues accept/reject feedback on code, API usage, and format; HarnessFix has a validation agent that checks scope, static correctness, and regression; FlowFixer uses LLM pre-execution assessments of semantics and relevance; RRSI has a diff critic that screens for leakage and inert machinery; Harness² has a composer that evaluates behavioral trajectory evidence. The prior claim that no paper uses a separate LLM to judge a repair is incorrect.

Where papers differ in generation: Harness-R1 and JIT-Agent train a repairer from execution outcomes rather than prompting one at inference time. RePAIR constructs rollback candidates by reverting components. FlowFixer uses symbolic constraint inference to rank nodes before LLM generation. DARC does not generate a patch; it profiles failure modes and prunes a fixed intervention library, selecting a frozen configuration with a verifier.

**Data point — AgentDefect.** The six program patches in the SelfHeal archive are human-authored. The 37 rows of `docs/agentdefect_component_table.csv` record what component each patch touches. The 14 scope names in `motivation_pilot/src/motivation_pilot/extension.py` `COMPONENTS` map each declared change to a code anchor. No LLM generated or judged these patches.

**Data point — AgentIssue-Bench.** `exp-2026-10-22/audit/boundary.json` records `loaded_implementation_verified` per run for case 594. The developer fix has 18 files. Three of 18 were loaded per run. In 15 of 18 runs the patch files were proposed but never executed. A generation method that produces a patch but does not confirm execution cannot tell whether the patch reached the code path it targets.

**Our method adds:** an execution check at the boundary. A change that touches a module with a probe is marked as executed when the probe fires in that run. A change in a scope without a probe is reported as not watchable.

---

## Q2 — What error and evaluation evidence papers use

Final task pass/fail is the primary deployment signal across all 21 papers, but many also use intermediate evidence at the patch-generation or acceptance stage. The prior claim that only CHILL-Harness and FlowFixer inspect intermediate information is incorrect.

Papers that use intermediate evidence at the generation or acceptance stage: CHILL-Harness records memory, tool state and environment state from offline checkpoints; HarnessFix uses step-level requests/responses, state effects, data/control flow, and source anchors; JIT-Agent uses compiler errors, interface mismatches, tool-call failures, and runtime exceptions; Self-Harness combines terminal verifier reasoning with mechanism evidence in traces; GEPA consumes textual evaluator feedback including compiler output; FlowFixer checks node outputs against inferred specifications and uses violation rates; DARC diagnoses specific action/procedure/format failure types.

The remaining papers use failed traces or benchmark outcomes as the primary signal, with no intermediate-state analysis during acceptance.

**Data point — 78383658 R experiment.** `motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22-r/decision.json`, field `coverage_per_run`. All 18 R runs (nine for original+R and nine for published+R, three inputs by three repetitions each) have `coverage_verified: true` — 12 documents retrieved and every catalog title present in the final model request. The adequacy of the four configurations is:

| configuration | adequacy |
|---|---|
| original | inadequate |
| original+R | adequate |
| published | inadequate |
| published+R | unresolved |

The published+R adventure input remains unresolved although its retrieval coverage was perfect in every run. The model boundary sits between the retrieval probe and the final output. A paper that reads only the final outcome sees published+R as "unresolved" and original+R as "adequate" without knowing that both cleared the same retrieval boundary. The difference in outcome must come from the model boundary, which is downstream of the boundary that was tested.

**Our method adds:** a boundary test between the patched module and the final check, with three reported properties: soundness (share of boundary passes whose final check passes), sensitivity (test fails on the buggy program and on each removal of a necessary change), and execution (the tested module ran in that run).

---

## Q3 — Does repair validation establish that the specific repair executed?

A rerun of a changed configuration establishes that the configuration was used. It does not, by itself, establish that every conditional repair mechanism activated on the test tasks. The question is whether existing validation checks close that gap.

The table column shows the range of answers across the 21 papers. Three papers are labeled yes with scope qualifiers. DARC distinguishes between interventions that were invoked and those that were not attempted, which is invocation-level confirmation. Harness² requires the composer to cite a specific trajectory moment showing the retained edit's mechanism; the confirmation is behavioral and qualitative, not instrumented branch coverage. ModularRSI gates on explicit execution of two sampled tasks and rolls back on failure; the confirmation holds for those two tasks and does not guarantee the modified function is reached on all validation inputs.

The remaining partial papers have checks with narrower scope. CHILL-Harness logs orchestration-decision routes and authorization decisions, which confirms the intervention level but not every internal edit activation. Harness-R1 assigns zero reward to inert or invalid patches, which distinguishes no-op patches from effective ones but does not establish per-conditional-branch coverage. ActiveSaddler has one case-study example of detecting a hook that never triggers on multiline replies, which is not a demonstrated universal gate. JIT-Agent confirms module invocation through protocol but conditional logic inside can remain unexercised. GEPA confirms the changed prompt is received when the module is invoked but does not verify instruction compliance. No paper requires proof that every conditional repair branch activated on the validation tasks.

The reasons this matters: first, sampled validation tasks may not reach the modified code path (ModularRSI executes on two randomly sampled tasks, which may not exercise the modified function). Second, prompt and context edits are included in the request when the module is invoked, but the model may not comply with or reach the instruction (GEPA, ACE). Third, as the 77178370 pilot shows, low enactment rates mean the with-arm versus without-arm comparison measures a mix of enacted and bypassed runs.

**Data point — enactment rate, 77178370.** Source: `motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl`, comparison_id `77178370:P_core|empty`. Only two of nine with-arm runs enacted P_core (π = 0.22). The with-arm versus without-arm contrast therefore measures a mix of enacted and bypassed runs, not the effect of P_core itself.

**Our method adds:** explicit three-way distinction: E (whether the edited mechanism executed in this run), Z (whether the intended intermediate boundary condition was met), and Y (whether the final task check passed). The enactment rate π = k_executed / n_with is reported alongside the effect estimate. No existing paper reports π or separates E from Z from Y for individual component comparisons.

**Separate question — which components are necessary (RQ3).** This is a different question from whether the repair executed. The data point below addresses it; it is not an answer to Q3 above, but it identifies a distinct gap.

**Data point — 79343179, 13 comparisons.** Source: `motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/comparisons.jsonl`, rows where case is 79343179.

| change | context | k_with | k_without | verdict | PN |
|---|---|---|---|---|---|
| L1 | empty | 0/3 | — | not assessed (parent not adequate) | — |
| L2 | empty | 0/3 | — | not assessed | — |
| L3 | empty | 0/3 | — | not assessed | — |
| L1 | L2 | 0/3 | 0/3 | not assessed | — |
| L1 | L3 | 0/3 | 0/3 | not assessed | — |
| L2 | L1 | 0/3 | 0/3 | not assessed | — |
| L2 | L3 | 0/3 | 0/3 | not assessed | — |
| L3 | L1 | 0/3 | 0/3 | not assessed | — |
| L3 | L2 | 0/3 | 0/3 | not assessed | — |
| L1 | L2+L3 | 3/3 | 0/3 | required | 0.86 |
| L2 | L1+L3 | 3/3 | 0/3 | required | 0.86 |
| L3 | L1+L2 | 3/3 | 0/3 | required | 0.86 |
| DV | L1+L2+L3 | 3/3 | 3/3 | removable | 0.00 |

Each Li is necessary only in the context of the other two. DV is removable in that full context. No existing paper tests each component in its admissible context or computes PN per component conditional on the context. The minimal sufficient set is {L1, L2, L3}; the baseline configuration is a larger sufficient set that includes a removable change.

---

## Q4 — Success criteria and measurement

**Evaluation setup.** All 21 papers evaluate on fresh task runs after the repair is applied. CHILL-Harness is the only paper that intervenes at runtime within a running workflow; the others apply the modified configuration before reruns. Candidate acceptance rules, final benchmark metrics, and execution-cost measurements are separate things and should not be counted as equivalent "criteria."

**Success criteria and repetition.** Several papers already separate multiple measurement types. JIT-Agent explicitly reports reward, latency, and monetary cost as three separate dimensions; bank retention requires strict improvement on at least one efficiency axis without degradation on others. ModularRSI reports four measures: Acc, Pass@3, Pass³ (all-three success), and StepNum. FlowFixer measures Repair Success Rate, Failure Attribution Accuracy, and Root Cause Accuracy separately; the latter two are not interchangeable with the first. RRSI reports paired task-bootstrap intervals alongside aggregate scores. The prior counts of single/double-criterion papers are therefore removed.

Repetition for uncertainty is also already present: AFlow executes each candidate five times; Self-Harness normally runs two evaluation attempts; ActiveSaddler reports mean ± SD over three test-time executions; RRSI uses paired bootstrap. These facts do not by themselves establish adequacy for the proposed repair verdict, but they rule out claiming that existing papers uniformly use one unqualified pass.

AgentIssue-Bench defines three criteria with distinct measurement types: (i) correctness judged by LLM, (ii) plausible resolution rate from running failure-triggering tests, (iii) reproduction rate from the agent resolving the issue. None of the 21 harness papers separates these three into distinct measured outcomes; each paper reports one combined task signal.

**Data point — P_core comparison, 77178370.** Source: `motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl`, comparison_id `77178370:P_core|empty`.

| field | value |
|---|---|
| k_with | 6 of 9 |
| k_without | 3 of 9 |
| Δ_mean | 0.30 |
| 95% interval for Δ | [−0.12, 0.67] |
| P(Δ > 0) | 0.92 |
| enactment rate π | 2 of 9 runs |
| recorded verdict | not assessed (parent not adequate) |

The interval crosses zero. P(Δ>0) is 0.92, below the 0.95 level. Only two of nine with-side runs enacted P_core (π=0.22). A paper that reports "6 of 9 passed versus 3 of 9 passed" without an interval treats this as a positive signal. The interval shows the direction of effect is uncertain. The low enactment rate shows the patch rarely reached the module it targets, so the contrast does not measure the patch's actual effect.

**Data point — survival summary.** Source: `motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/summary.json`. Of the 88 comparison rows: 22 are recorded as required_in_context and all 22 survive at P(Δ>0) at or above 0.95. Eight are recorded as removable_in_context and none survive at P(|Δ|<0.2) at or above 0.95. Three runs cannot bound the removability margin at δ=0.2; about 12 runs a side are needed. No harness paper reports this gap.

**Our method adds:** the label procedure computes the Jeffreys posterior per cell, the effect Δ with its interval, the execution rate π, and the complier causal effect Δ/π. A required verdict needs P(Δ>0) at or above 0.95. A removable verdict needs P(|Δ|<0.2) at or above 0.95. Three runs settle required verdicts where the evidence is clear (P(Δ>0)=1.00 on 3/3 vs 0/3) but cannot settle removable verdicts.
