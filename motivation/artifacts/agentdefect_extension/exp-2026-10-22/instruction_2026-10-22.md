# Jun's instructions for exp-2026-10-22, verbatim

Copied from the Claude Code session transcript `bfa6256c-ee74-43c2-8488-9086ca46b071.jsonl`.

## Pasted plan and RQ statement (2026-10-22T12:53:39.731Z)

please find the new plan for the new pilot experiment, validate if match with agent defect rq "A successful harness patch establishes that one configuration works. It does not establish which component changes are necessary, which depend on other changes, or whether another repair scope would satisfy the same requirements."
"

<pasted_content id="3e5f">
AGENTDEFECT MOTIVATION PILOT — CODING-AGENT IMPLEMENTATION PLAN
22 October 2026
Status: new extension specification. This document does not report new executions.

TASK

Extend the existing AgentDefect motivation pilot to answer:

Among the existing complete repairs, which persistent component changes are required for adequate recovery, which are removable or depend on other changes, and does measuring these relationships change the repair we would keep?

Use the existing programs, assets, executed patches and frozen checks. Reliable behavior across the declared inputs is the primary requirement; smaller repair scope matters among adequate configurations. Produce a reproducible configuration table, targeted intermediate observations and a concrete repair decision for each evaluable case.

This is an exploratory motivation study. Do not restart donor matching, build a graph learner, generate synthetic failures, fabricate model/tool responses, or treat repair minimization alone as proof of the proposed method's advantage.

1. START FROM THE CURRENT LOCAL PILOT

Known project locations, to verify on the execution host:
- working tree: /data/wang/junh/githubs/AgentDefect/motivation_pilot
- Python: /data/wang/junh/envs/harnessfix/bin/python
- historical repository: https://github.com/JuneHou/harness-detect
- historical experiment: repair_family_pilot
- historical comparison commit: cb39baa2f8793cf9573dc301c5e74a376b7eeb26

Read applicable AGENTS.md and current local contracts, manifests, reports, runner and CLI. Resolve the actual Git root, source revision and dirty state. Do not overwrite existing work.

The remote main branch inspected for this plan exposes an older repair_family_pilot preview; motivation_pilot/README.md was not accessible there. The current local implementation is therefore the authority for commands, file paths, selected cases, completed runs and budgets. Do not execute old placeholder commands on the assumption that they implement the extension.

Preserve any later explicit user decision found in the project record, including a later scope restriction for 79343179. Record its provenance. An assistant recommendation or stale default alone does not supersede a user-selected scope. Resolve this from available records without adding a new confirmation gate.

Locate:
- exact original/published program pairs and data assets;
- current case IDs and aliases;
- baseline patches, all retained revision attempts and audit variants;
- frozen original, related-input and preservation checks;
- subprocess execution, model adapters, existing local_checks and log readers;
- model-call/token accounting, cache keys and NUMBERS.md if present.

Write implementation_map.json with verified entrypoints and artifact paths. Read actual CLI argument handling; an earlier development report identified an ignored --config argument. Confirm that the effective configuration matches the selected file before collecting evidence.

Inventory all currently enrolled AgentDefect cases. Keep already-passing and environment-blocked cases visible. Do not import the AgentIssue-Bench five-case report, repository patch arms, Docker oracle rules or benchmark counts.

2. WHAT CHANGES FROM THE OLD PILOT

Old output:
A complete repair passed or failed the public/frozen checks.

New output:
The same checks, plus:
- a fixed functional-component map;
- a manifest of concrete persistent edits;
- coherent with/without comparisons;
- observed producer state, consumer input and downstream behavior;
- a scope decision with evidence and an explicit uncertainty statement.

Keep two findings distinct:
A. Public-check success with failure on a valid related input demonstrates an adequacy gap.
B. A controlled comparison of concrete edits can show which changes must be retained or removed.
Finding A alone does not establish causal module targeting or a graph benefit.

Start with existing complete repair routes. Do not author a new prompt/retriever/loader repair simply because that boundary lacks a candidate. A missing comparison is an explicit limitation.

3. CASE-SPECIFIC EXECUTION PLAN

Resolve exact source filenames and existing patch hashes from the local inventory. The table below names known cases and source-inspection priorities; it does not supply new outcome labels.

Case 76906469 — conversational memory/interface
- Preserve the historical original/A/B/AB table and its original model/settings.
- A changes memory to return message objects.
- B changes the agent to the conversational variant and also changes parsing-error handling in the recorded implementation. Preserve the exact existing B patch and acknowledge that bundle.
- Run original, A, B and AB on the published two-turn conversation only: the capital-of-France question followed by the question asking what was asked previously.
- Three fresh repetitions per arm: 12 episodes. This does not imply 24 actual model calls.
- Capture memory before and after each turn, actual request messages reaching the model backend, replies, exceptions and call counts.
- B's known message-format exception may occur before any model request. Record model_input=null with reason=no_model_call_due_to_interface_failure. Do not invent a model-input record.
- Retain the historical substring score for comparability and record its exact predicate from code. If it is only a France word check, label that limited endpoint; inspect the actual second answer separately. Do not silently upgrade historical scores to verified semantic memory recovery.
- Treat the four arms as a dependency diagnostic. AB may be the coherent deployable route; B alone is not automatically a valid standalone complete repair.
- If matching instrumented reruns already exist, reuse them by fingerprint instead of rerunning. Do not pool new gpt-6-luna runs with historical gpt-4-0613 counts.

Case 79343179 — spreadsheet loading
- Preserve original, existing baseline and published loader variants.
- Retain the historical direct load_excel_response comparison as scope=loader_only. In that scope, model-input and memory fields are not_applicable, not missing model traces.
- Measure rows retained, column names, user identifiers and the required Sentiment/Location values against the actual frozen spreadsheet. Verify the reported dropped-row behavior from artifacts rather than copying it as a new result.
- The earlier choice marked a full-agent sandbox with a shell stub. Implement this as a separately qualified scope=sandbox_full_agent; keep loader-only controls and do not pool the scopes.
- Use the real loader, agent and python_repl under the existing isolated runner. Replace ShellTool with the same refusing stub in every full-agent configuration: log the requested command, refuse execution explicitly and return no fabricated successful tool result.
- Capture the actual model requests, tool requests/results and final response. Use the previously frozen related inputs, including Sentiment and Location per row where specified in the contract.
- If shell refusal prevents completion, report that observed limitation. Do not restore unrestricted shell access or count a refused operation as successful.
- First establish the original/reference behavior in this environment. Full-agent results support only this declared sandbox scope; loader success alone cannot establish full-agent recovery.

Cases 77099194 and 78383658 — existing revision comparisons
- Retain original, baseline, both recorded revision attempts and published fix for each case; deduplicate identical content without dropping provenance.
- Verify each case's actual source responsibility and input-to-output path before assigning labels.
- For retrieval changes, record the query, retrieval settings, returned document IDs/text and the context actually sent to the model.
- For output-format/agent changes, record the model response before parsing, parser input/output, exceptions and the final returned result.
- Inspect retrieval depth and prompt instructions where implicated; do not create a new repair at either boundary merely to fill a table.
- Earlier proposed multi-query/depth combinations are not executed evidence unless their corresponding artifacts exist.

Case 77178370 — existing audit variant
- Retain original, baseline, published fix and the executed audit variant.
- Inspect whether retrieval, agent construction, memory and prompt responsibilities are independently changed.
- Observe the actual data path affected by each concrete candidate.
- Separate any variant whose instructions or test harness exposed answers. An answer-leaking execution is an audit finding, not recovery evidence.

Remaining enrolled cases, including 76897509, 78366661 and 78838421 where present
- Resolve their actual source/program names from the inventory.
- Use existing original/baseline/published variants and checks.
- Source-inspection leads include filtering, retriever implementation and mixed component changes; confirm these from code.
- For a retriever that returns an empty result without a model call, record that execution directly; do not infer an LLM failure.
- Preserve Ollama or other environment limitations as blocked/unknown where unresolved. Do not silently replace required backends to obtain a passing case.
- Keep already-passing programs as descriptive controls; they do not demonstrate repair recovery without a reproduced failure.

Across the reported buildings, action-movie and family-movie cases:
- Keep the corrected frozen checks and original task assets.
- Do not include expected answer lists in repair instructions, agent prompts or evaluator-injected context.
- Allow normal access to the program's intended source documents. Distinguish that legitimate access from evaluator answer leakage.
- Preserve old leaked runs for audit and exclude them from new recovery summaries.
- Evaluate the actual returned behavior. Code-string matching cannot stand in for the PDF search result.

4. FREEZE REQUIREMENTS, COMPONENTS AND ACTIONS

A functional component is a responsibility with an interface, such as:
document selection; retrieval; memory representation; prompt assembly; agent control; tool/loader implementation; output parsing.

It is not automatically a Python file. Several components may live in the same small program. Do not use changed-file count as the primary scope measure.

For each component freeze:
component_id, responsibility, source symbols/anchors, input/output contract, observable boundaries.

For each concrete change freeze:
change_id, patch/code hash, base identity, component_ids, provenance,
preconditions, coupled changes and intended effect.

A published fix is a reference candidate, not a minimality label. Two edits to the same component are distinct changes. If an edit cannot be separated from compatibility glue, keep it as a coupled change unit and avoid unsupported individual attribution.

For every check freeze:
check_id, original/related/preservation category, source of requirement,
input and asset hash, expected behavior, validity status,
required_for_adequacy, execution scope and oracle version.

Prefer existing valid checks. Do not create another question collection. A newly discovered invalid oracle gets an explicit versioned correction and affected reruns; it is never silently replaced after seeing candidate outcomes.

Adequacy requires passing all frozen required checks in the declared scope and no confirmed new regression on the preservation checks. Report each outcome separately. Unknown on a required check makes adequacy unresolved. Optional diagnostics do not become new failure requirements after the fact.

5. BUILD THE CONFIGURATION MANIFEST

For each qualified case enumerate:
- original;
- every existing complate route listed above;
- a coherent reduction of a multi-component route when it tests a named contribution;
- a compatible combination of existing actions only when a stated hypothesis gives it meaning.

Do not mechanically split every file or hunk. Two patches with disjoint edited symbols may still be incompatible. Conversely, multiple edits within one file may be independently meaningful.

For multi-component candidate P, first inspect P minus each separable change. With at most three separable change units, enumerate all coherent subsets if within existing resource limits. Otherwise declare the evaluated subset domain and make no exhaustive-minimality claim.

The manifest must identify:
configuration_id; exact selected changes; effective component set;
coherence rationale; expected interface preconditions; inputs/checks;
execution scope; number of repetitions.

A malformed fragment or failed application is not evidence of behavioral coordination. A well-formed persistent change that exposes an actual incompatible interface can be informative, provided it is clearly classified.

If conflict resolution would add new repair behavior, stop that combination as outside the existing candidate domain. Do not hide such edits in instrumentation or the runner.

6. INSTRUMENT THE ACTUAL EXECUTION PATH

Use focused observational hooks shared across variants. Avoid blanket argument logging and coverage-only conclusions.

Capture, when exercised:
- loaded program/module path and content hash inside the worker;
- source asset identities;
- retrieval query/settings and returned evidence;
- memory snapshot before/after calls;
- final request messages at the actual backend boundary;
- actual tool calls/results;
- pre-parser output, parsed output and final answer;
- exception stage and actual model-call/token usage.

Do not log a locally constructed prompt as if the model received it. A zero-call run must have zero observed requests. A missing trace is unknown unless the control flow establishes why the stage did not execute.

Use safe snapshots that do not mutate program state. Separate instrumentation from repair code and save its hash. Confirm original/reference required outcomes with and without probes on the first development case. Changed behavior invalidates the relevant observational comparison until resolved.

Verify that each test imports/executes the selected variant. A cached module or hard-coded published loader can produce false recovery. Use fresh subprocess state and record loaded identities at the execution boundary.

Keep raw model responses and tool outputs rather than only pass/fail. Store judge explanations separately from the evidence being judged.

7. EXECUTION AND RESOURCE SETTINGS

Use the existing subject-model adapter. The previously selected new-run model is gpt-6-luna at temperature 0, unless a later explicit project decision supersedes it. Record the actual backend/model for each new cell. Do not change existing published/ historical labels when using a new model.

No new repair-writing calls are needed for this extension: candidate patches already exist.

Reuse current authorized budgets, credentials and timeout settings. Do not introduce a zero-paid-call default or copy the AgentIssue-Bench written-go gate into this experiment. Record the expected episodes and check executions before running; actual calls/tokens may differ substantially.

Use three fresh repetitions per new configuration/input cell unless the current frozen AgentDefect protocol explicitly specifies otherwise. Preserve the 76906469 four-arms-by-three design.

Retain the current retry policy. If no policy is present, permit one additional attempt only for a transient connection, rate-limit, provider-server or transport timeout error. A wrong answer, interface exception, malformed patch or behavioral failure is not retried as infrastructure failure. Save both attempts and account for both.

Execute in this order:
1. Inventory and reuse eligible current artifacts.
2. Run the 76906469 instrumentation path and verify its evidence records.
3. Run qualified existing complete repairs on the frozen checks.
4. Run the frozen coherent reductions/combinations.
5. Run the separately qualified 79343179 full-agent sandbox scope.
6. Derive comparisons and regenerate the report.

Complete the declared existing cohort, retaining failures and unknowns. Do not expand the cohort or author new repairs to obtain a desired interaction.

Reset memory, caches, temporary assets and task state between episodes as required by the original program. Keep code, input, fixtures and settings matched across each comparison. Record seeds where available, without claiming hosted-model determinism.

Fingerprint cached runs by:
program/base hash, patch set, assets, input, scope, model/backend settings,
dependencies, initial state, probe version, oracle version, protocol version and repetition.
A changed scope or model invalidates reuse as a matched run.

Classify behavioral failure, candidate-induced interface/runtime failure, infrastructure failure, application failure, oracle invalidity, environment block and unresolved timeout separately.

8. MEASURE CONTRIBUTION AND REPAIR CHOICE

For a specific concrete change m, compare C+m against C with all other changes, inputs, checks and scope matched.

When C+m is adequately recovering:
- required_in_context: removing m causes a confirmed loss of adequacy;
- removable_in_context: the reduced configuration remains adequate;
- unresolved_in_context: evidence is insufficient or inconsistent.

Aggregate for that same concrete change over declared evaluated contexts:
- useful_observed: required in at least one context;
- conditionally_necessary_observed: required in at least one and removable in at least one;
- redundant_within_evaluated_contexts: at least one pair, all declared evaluated contexts removable, no unresolved context;
- unresolved evidence: report directly.

Conditional necessity is a subtype of usefulness. Use separate fields and counts rather than forcing them into disjoint categories. Do not generalize from one concrete edit to every possible repair in its component.

A recovering configuration with all single deletions failing is only locally minimal under those deletions. Claim inclusion-minimality only if every coherent proper subset in the declared domain was evaluated. Otherwise say "no successful evaluated reduction."

For stochastic cells report x/3 and all raw outcomes. Use 3/3 as the pilot's observed-pass rule where consistent with the frozen protocol; mixed results remain unstable/unresolved for necessity claims. Three repetitions are not a proof of general reliability or a significance test.

Separate:
- adequate alternative complete routes;
- compatibility dependence;
- removal of unnecessary changes;
- public/related-input adequacy gaps;
- possible source repair versus downstream compensation.

Compensation requires evidence that the source condition persists while its consequence is prevented through the proposed route. If the source invariant is itself required, leaving it violated makes the candidate inadequate. Ordinary A/B compatibility is not automatically compensation.

Use the observations to state the decision:
retain both; remove a specified change; choose an adequate existing alternative;
keep the broader candidate; or remain unresolved.
Compare that with the decision justified by the old public-check result.

Say whether intermediate observations were needed, or whether direct ablation or interface inspection already sufficed. The latter is a valid result and a necessary limit on the proposed method's motivation.

9. IMPLEMENTATION AND REQUIRED OUTPUTS

Extend existing modules under motivation_pilot/src/motivation_pilot where appropriate. Exact new filenames are implementation choices; do not add a parallel evaluation framework.

Use a fresh versioned artifact directory, for example:
motivation_pilot/artifacts/agentdefect_extension/<experiment_id>/

Required artifacts:
- implementation_map.json
- inventory.jsonl and qualification.jsonl
- experiment_manifest.json with effective settings and run budget
- cases/<id>/contract.json
- cases/<id>/components.json
- cases/<id>/actions.json and configurations.json
- cases/<id>/probe_spec.json
- hypotheses.jsonl, frozen before new outcomes and marked exploratory
- runs.jsonl with immutable raw observations/stdout/stderr/responses
- comparisons.jsonl
- contribution_verdicts.csv
- report.md and limitations.md

Record prior exposure to existing candidate outcomes. Hypotheses written now are not held-out predictions merely because they precede a rerun.

Each run needs:
case/configuration/input/scope/repetition IDs;
code/asset/patch/probe/check hashes;
loaded implementation identity;
effective model/environment;
raw request/response and observation paths;
execution status;
public/related/preservation results;
adequacy and uncertainty;
attempt count, elapsed time, observed calls/tokens or an explicit unknown reason.

Each comparison needs:
concrete change ID, unchanged context, with/without run IDs,
matched-condition checks, per-requirement differences,
contribution verdict, mechanism evidence, decision and claim limit.

If the project uses NUMBERS.md and a number-check script, register every reported count and run that check after report edits. Do not derive counts from planned calls.

Validate against actual recorded traces and real qualified executions. Do not introduce synthetic cases or fake traces into this pilot. Target checks at loaded-variant mistakes, pre-call exceptions, stale caches, mismatched comparisons and unknown-to-failure conversions.

10. REPORT AND STOPPING CRITERIA

The report must include:
1. Case flow, execution scopes and qualification limitations.
2. Existing complete patches versus original/related/preservation outcomes.
3. Coherent reduction/combination results with component sets.
4. Observed intermediate effects and mechanism uncertainty.
5. The concrete repair decision before and after the new evidence.
6. Executions, actual model calls/tokens and reuse of historical artifacts.

For 76906469, show old and new tables separately.
For 79343179, show loader-only and sandbox-full-agent tables separately.
For revision cases, retain every existing attempt, including inadequate and leaked historical variants with clear exclusions.

Count independent underlying programs separately from inputs, patches and repetitions. Do not make unsupported prevalence claims from the selected pilot.

The pilot is complete when every frozen feasible cell has evidence or an explicit unresolved reason, verdicts can be reproduced from the records, and each case has a justified decision or limitation. Finish and report negative results rather than seeking favorable examples.

Allowed conclusions:
- a particular edit is required/removable in evaluated contexts;
- adequate existing routes differ in scope;
- a public-check success fails a valid additional requirement;
- intermediate evidence explains a dependency;
- the new evidence changes, confirms or cannot resolve the selected repair.

Not established by this experiment:
- all repairs at a component scope fail;
- universal minimality;
- compensation from a compatibility exception;
- donor prediction, learned graph benefit, HarnessFix superiority or paper-level novelty.

The first sentence of the final scientific report should answer:
"What specific repair decision does this extension justify that the old whole-patch scores could not?"
</pasted_content id="3e5f">

"

## Corrections (2026-10-22T13:33:30.426Z)

Make these six corrections.

1. Add an admissibility gate before calculating contribution verdicts.

The current rule immediately labels a change required when its parent is adequate and its removal is inadequate. It omits the earlier requirement that the comparison isolate the intended change and produce a coherent configuration.

Use this sequence:
First establish comparison admissibility: matched execution conditions, intended implementation loaded, exactly the declared action difference, valid checks, and coherent remaining implementation. Then assess whether the parent adequately recovers. Only then calculate required, removable, or unresolved.

Keep 76906469 B as an interface-dependency diagnostic. Its expected representation mismatch is useful evidence, but an incompatible fragment must not become evidence that an entire module scope cannot repair the problem.

Also resolve an ambiguity in “fewer than three repetitions completed.” A candidate-induced exception can be a completed experimental observation even though the program never returns an answer. Infrastructure failures, missing observations, and invalid fragments must remain distinguishable.

The blanket status rules need adjustment:
- ModuleNotFoundError is not always an environment problem; a candidate may introduce the invalid import.
- Any other nonzero exit is not automatically a candidate interface failure; instrumentation or evaluator code may have failed.
- oracle_invalid needs an actual qualification rule, not just a status name.
2. Fix the 78383658 U1 removal and verify every patch decomposition.

U1 is defined as the response schema, parser, format instructions, and their integration. However, published_minus_U1 removes the parser from the chain and removes format-instruction references while apparently retaining schema/parser construction and associated imports.

That is not removal of the complete declared U1 action. The retained construction could still affect execution, and its code still affects the claimed repair scope.

Either:
- Remove the complete U1 unit, including initialization that exists only for that unit; or
- Rename and redefine U1 as the narrower intervention actually performed, explicitly retaining the remaining changes.
For every decomposition, check:
The declared action set reconstructs the complete candidate, and each matched comparison differs only by its declared action.

ast.parse and unique string matching verify syntax and replacement mechanics. They do not establish this causal isolation or runtime coherence. Apply this check to P1/P2 and P_core/P_sys as well.

3. Change the instrumentation specification to capture methods that actually execute.

Wrapping BaseChatMemory.load_memory_variables or BaseOutputParser.parse does not guarantee interception when concrete subclasses override those methods.

Resolve and instrument the implementations used by each configuration, including relevant alternative execution paths. Add a small verification that each expected boundary produces an event when reached.

The trace should distinguish:
- Boundary reached and observed.
- Boundary not reached because execution stopped earlier.
- Boundary removed or rerouted by the candidate.
- Observation unavailable because the probe did not cover the path.
Also, _get_request_payload records request preparation. It does not prove that a network request was sent. Record preparation and actual backend attempts separately, including retries. Preserve tool-call fields and identifiers when they are part of the request, rather than retaining only role and content.

Finally, an exception plus no request event does not always mean “interface failure.” Derive that reason from the classified failure stage.

4. Make the behavioral contract explicit before assigning adequacy.

The current contract builder marks every check required_for_adequacy: true, while copying validity from an existing file. Add a qualification gate: unresolved or invalid checks cannot support a recovery verdict.

Two cases require especially clear wording:
Case	Required clarification
78383658	State whether the original overview-fragment check is required or descriptive. Preserve its result separately from the title-based requirement; do not silently substitute one public-check definition for another.
78366661	A nonempty passage list establishes the narrow reproduction endpoint. It does not establish passage relevance or complete PDF-search recovery.


For cases without preservation checks, report that coverage as absent. Do not imply preservation was established merely because the available endpoint passed.

5. Freeze the repair-selection rule and distinguish actions from modules.

The plan specifies contribution verdicts but does not yet fully specify how they change which repair we retain, the pilot’s central question.

Add a decision record for each case:
Initial candidate and selection basis → new comparison evidence → retained candidate or unresolved choice → change in adequacy, functional-module count, and action count.

Freeze the initial choice before new outcomes. Exclude inadequate candidates and leave unresolved candidates unranked. Define how ties are handled.

Crucially, L1, L2, and L3 all belong to the loader module. Removing L3 may reduce the number of repair actions while leaving the changed-module count at one. Report that as a smaller action set, without claiming a smaller module scope.

Minimality also requires conclusive results for all relevant coherent proper subsets. Merely scheduling all subsets is insufficient if some remain unresolved.

6. Add intermediate predictions to the hypothesis table.

Most current predictions concern final pass/fail outcomes or contribution labels. That does not fully support the proposed investigation of propagation mechanisms.

For each relevant comparison, specify before execution:
Which intermediate state should change, which should remain unchanged, and which observation would contradict the explanation.

For example, the U1 comparison should distinguish changes in retrieved documents, model-visible formatting instructions, raw model output, and parsed output. This lets the report determine whether intermediate evidence contributed anything beyond the endpoint comparison.

Keep these predictions exploratory. Recording them before reruns does not erase prior knowledge of the cases.

A few smaller corrections are also needed:
- The arithmetic is 171 scheduled episodes: 141 in model-enabled scopes and 30 loader episodes, before retries. Replace “141 model-calling runs”; B may make zero calls.
- Include initial-state identity and the effective generated configuration hash in fingerprints.
- Do not equate not_repaired with “already passing”; use the recorded qualification reason.
- The attachment references “Order of work step 6” and “Verification”, but those sections are absent. Add the runnable command, required offline checks, resume behavior, and execution/cost cap.

## Message (2026-10-22T13:44:56.271Z)

The user answered: "What cap should stop the live run? The hard execution cap is already fixed at 174 scheduled episodes plus at most one retry each (max_retries_per_execution: 1 in study.yaml). The dollar estimate below uses the pilot's own price constants in pilot_run.py ($0.10 per million input tokens, $0.50 per million output tokens), which I have not verified against current pricing. The 10-20 pilot used 10,173 input and 1,373 output tokens over 54 runs."="i don't need you tell me cap, i need estimated cost". Read the answers carefully — they may request clarification, changes, or that you not proceed — and follow what they actually say.

## Message sent during a turn (2026-10-22T13:45:49.593Z)

no retry.
