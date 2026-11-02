# Harness repair verdicts as causal estimands

Research question. A successful harness patch establishes that one configuration works. It does not establish which component changes are necessary, which depend on other changes, or whether another repair scope would satisfy the same requirements.

Every number in this report is read from the experiment records listed in section 6 and checked against their registries.

## 1. Problem and proposal

The 20 harness repair papers of the literature review (`docs/Agent_Error_Mitigation_Review (1).html`) change a persistent system, its code, prompt assembly, tool adapters, memory policy and control rules. They accept a patch when the patched harness passes its test. The review leaves three questions open. Whether an intervention was enacted at all, as distinct from being wrong (DoVer, row 15). Whether a component's effect can be separated from stochastic recovery, with intervals (Causal Agent Replay, row 6). Whether alternative and jointly sufficient repair sets can be recovered under validity constraints (MRFR and GCJR, row 22).

Two motivation experiments show that the acceptance test leaves all three open. A verdict such as "this change is required" or "this change is removable" is a thresholded contrast of two pass counts, three runs a side. The runs may never have executed the change.

**Proposal.** Define the verdict on a harness change as a causal estimand and estimate it. The estimand is the effect of the change on the pass probability, among the runs that enact it, in its repair context. Its uncertainty is valid at whatever repetition count the loop stops. Three claims follow.

| claim | statement | review cell |
|---|---|---|
| 1, enactment | A change is received only when the run's path executes its module. A verdict that ignores receipt credits or blames a change that never ran. | DoVer, row 15 |
| 2, repetition | The three of three rule mixes the change's effect with resampling noise. Pass probabilities with intervals and a stopping rule replace it. | Causal Agent Replay, row 6 |
| 3, sufficient sets | The unit of a repair decision is a minimal sufficient set of changes in context, and a case can hold more than one. Interface constraints make some sets inadmissible. | MRFR and GCJR, row 22 |

A fourth observation, that a pass can come through a path the repair never touched, is recorded in section 3. This is the condition under which tool invocation alone cannot serve as an exact substitute for the final check: the task can succeed without the tool running.

## 2. Datasets and experiments

**AgentDefect** holds 37 case folders of small LangChain programs with a reported defect, 36 with a buggy and a fixed program, and a median substantive diff of 8.5 lines. Six programs ran. Each complete repair was decomposed into declared changes by statement level AST comparison. Every coherent subset was built as a configuration. Each pair of configurations that differs by one change was run three times per frozen input on gpt-6-luna, with probes at the module boundaries. The main experiment holds 174 runs and 32 comparisons, the retrieval intervention 36 runs and four comparisons, and the environment experiment 192 runs and 52 comparisons. All 402 runs carry boundary states and a trace.

**AgentIssue-Bench** is a cohort of 50 reproduced issues in real agent repositories with Docker images and developer fixes. Qualification produced 36 records, 30 of which reproduced the failure, and five cases qualified for the removal study with their controls held. Each developer fix was split into changes and every removal was run three times per check. The record states per run whether the implicated code was reached and the loaded implementation was verified. The removal study holds 42 comparisons and its corrected follow-up 19.

**Reanalysis.** Every recorded comparison of both datasets, 88 and 61 rows, was re-read without a model call. Each side's passes over its runs give a Jeffreys Beta posterior of the pass probability. The effect is the posterior of the difference between the with side and the without side, and each with side run is marked enacted or not. A required verdict survives when the posterior probability of a positive difference is at least 0.95. A removable verdict survives when the probability that the two rates lie within 0.2 is at least 0.95. Fisher's exact two sided test is reported beside the posterior.

## 3. Evidence for each claim

### Claim 1, enactment

| dataset | evidence |
|---|---|
| AgentDefect | The 77178370 published repair adds a retrieval tool. Across its nine with side runs it passed six, and two executed the tool, so four passes came from runs that never took the repair's path. The 76906469 change B alone stops at the memory interface before any request in all four of its rows and enacted nothing. Of 88 rows, 73 have an observed enactment rate, four never enacted, and 11 touch document splitting, the model client or data loading, modules without a probe, so their rate is undefined. |
| AgentIssue-Bench | All 552 with side runs enacted their change, because qualification required the fixed files to load and the implicated code to be reached. Where receipt is enforced the dilution disappears. The two datasets differ in exactly the quantity the claim names. |

**Why the 77178370 passes mislead.** The archived acceptance test asks what buildings are made of and accepts any answer that contains the word brick. The program is built to answer from seven retrieved notes through a document search tool, and one note states that buildings are made of brick. A model answers this question from its own knowledge, so the test passes whether or not the tool ran. Six of the nine with side runs passed and two executed the tool. The test cannot separate a pass through the repair from a pass without it. The remedy is a stronger check that swaps in notes without the answer, so that only the retrieval path can pass. A pass without the tool shows the test is too weak. It does not show that no repair was needed.

A verdict needs the enactment rate beside it. A repair loop needs probes at the modules it edits, or it cannot tell a never executed change from an ineffective one.

### Claim 2, repetition

| dataset | evidence |
|---|---|
| AgentDefect | The configuration published+R passed the adventure input two of three times in one fresh batch and three of three in the next, and its verdict moved from not assessed to removable. None of the eight removable verdicts survives at the margin 0.2. Three passes against three leave a probability of 0.72 that the two rates lie within 0.2, and nine against nine leave 0.95. Of 22 required verdicts 17 rest on three runs a side, where Fisher's exact test gives p = 0.10 and the posterior gives 0.996. Only the five 78383658 rows with nine runs a side are significant under both. |
| AgentIssue-Bench | Of 13 removable verdicts 11 survive at 0.2, all with 12 runs a side over four required checks, and the two with nine runs a side fail. At the margin 0.1 none survives in either dataset, since 12 against 12 gives 0.86. All 25 required verdicts rest on three target runs on the without side, with Fisher p = 0.10 and posterior 0.996. |

Three repetitions cannot establish that a change is removable, and establish that it is required only under a prior dependent rule. The repetitions a verdict needs are a quantity to compute per comparison. When both sides pass every run, removability at the margin 0.2 needs about 12 runs a side and at 0.1 about 24. The loop should stop when the posterior clears its level.

### Claim 3, sufficient sets

| dataset | evidence |
|---|---|
| AgentDefect | In 79343179 the three loader changes L1, L2 and L3 are each required given the other two, and all six proper subsets are inadequate, so L1L2L3 is inclusion minimal. The developer's four change baseline contains the removable docstring change DV. In 78366661 two routes are adequate, the one change baseline and the published N+P1 with three modules and two changes, and the scope rule keeps the smaller. In 76906469 B alone breaks at the memory interface, so the set {B} is a positivity violation and only {A, B} can be assessed. The measured verdicts changed the retained repair in four of six cases. |
| AgentIssue-Bench | In evoninja_515 the routing change is removable and the smaller repair is kept. In evoninja_525 the two type changes are removable on the runtime checks and required for the package type check, so the sufficient set depends on the declared requirement. In evoninja_504 and evoninja_594 every proposed reduction is a malformed fragment or leaves names undefined, so no alternative set is admissible. After the corrections one of five cases keeps a smaller repair. |

The decision object is a set. Minimality, alternative routes and inadmissible combinations all appear in the records, and the repair loop needs a rule that ranks admissible sufficient sets by declared scope.

### Evidence in the published artifacts

Each claim has at least one instance that needs no run of ours. The instances below sit in the archives, images and result sheets the dataset authors published.

| observation | where it sits | model involved | claim |
|---|---|---|---|
| Every AgentIssue-Bench verdict, the removable routing change in evoninja_515, the removable type changes in evoninja_525, the malformed fragments in evoninja_504 and evoninja_594, and enactment enforced on every run | the authors' Docker images, developer fixes and checks. All 315 scored runs made zero model calls | none | 3, and 1 |
| L1L2L3 inclusion minimal, DV removable, the developer baseline not minimal (79343179) | the archived loader code under pandas, loader scope only | none | 3 |
| B alone inadmissible (76906469) | the archived program raises the LangChain memory error before any request | none | 1 and 3 |
| The acceptance test is blind to enactment (77178370) | the archived test.py asserts only that the word brick appears in the answer | none | 1 |
| Acceptance by one pass with retries, and the same case resolved under one model and not another | the authors' own result sheets. 79343179 resolved by Gemini on attempt two and by neither GPT-5.2 nor Claude, 78366661 by Gemini only, 78383658 by Claude only on attempt two, 77178370 only in two ablation settings, with attempts running to three | the authors' models | 2 |

The runs of section 3 under gpt-6-luna illustrate the same claims under a model the authors did not use. The archived programs name gpt-4, gpt-4o-mini and gpt-3.5-turbo, and gpt-4 is withdrawn at the endpoint, so the authors' exact condition is partly beyond reproduction.

### A fourth observation

The 77178370 published agent answered from the model's own knowledge, with no retrieved note in any request. The observed successes without tool invocation show that invocation is an insufficient substitute for the current final check. The task can succeed without the retrieval module running, so invocation and final success are different endpoints. Whether conditional independence holds and whether richer boundary information can estimate the final repair effect remain unresolved. The corresponding estimand is a path specific effect, measured by swapping the retrieved notes for notes without the answer. Its estimation is future work.

## 4. Method

The method is a validator of a proposed harness patch. It replaces the accept step of a repair loop, the point where one pass of one check accepts the patch. The patch generator and the task check stay as they are.

### 4.1 Modules, boundaries and the module graph

A module is a code unit between two probe boundaries. A probe records the state that enters the module and the state that leaves it, so a module is a mechanism with an observable input and output by construction. The instrument records eight boundaries, memory, the prepared chat request, the network attempt, the parser, tools, embeddings, retrieval and the loader. An edit scope, the lines a declared change touches, maps onto one or more modules through its code anchor. A scope without a probe on both sides is not observable, and a change there is reported as such. In the six programs that holds for document splitting, the model client and data loading.

Each module also carries a functional label for comparison with the literature. The labels are the five ModularRSI modules, Agent Loop, Observation Management, Tool Use, Context Management and Task Completion Detection, and a sixth, Retrieval Pipeline. ModularRSI decomposes a terminal agent and names no loading, indexing or retrieval stage, while 15 of the 37 AgentDefect cases change chunking, the vector store, retrieval or document metadata. The 14 scope names of the pilot map to the labels as follows. Appendix A lists how each related work defines a module.

| functional label | pilot scope names | basis in ModularRSI section 3.2 and appendix B |
|---|---|---|
| Agent Loop | agent_control, chain_control, execution_control, prompt, output_parsing | the loop controls the reasoning, action and observation cycle, constructs the prompts for the model and hands parsed commands on |
| Tool Use | tools | tool selection, invocation and validation |
| Context Management | memory, memory_representation | interaction history, its retention, compression and retrieval |
| Observation Management | none among the six programs | environmental feedback is filtered or compressed before it re-enters the loop |
| Task Completion Detection | none among the six programs | decides whether the task is complete |
| Retrieval Pipeline, added | loader, data_loading, document_splitting, vector_store, retrieval | no counterpart. Added for the document pipelines of the dataset |
| infrastructure, outside the modules | model_client | sandbox initialization, parallel execution and LLM communication stay outside evolution |

The module graph is read from the recorded data flow of a run, in the order the run visits the boundaries. It is not read from the edit scopes. For the six programs the graph is a chain. It has one branch where the model chooses whether to call a tool, and one loop across conversation turns through the memory state. ModularRSI's modules form a star around the Agent Loop with no fixed order, which is a statement about edit scopes, and the two views coexist. The chain is what the reuse results of section 4.3 need.

### 4.2 A run as a structural model

A run on input x is a sequence of boundary states. Each module is a mechanism from the state entering it to the state leaving it. The final check reads the last state.

```
B0 = x
Bk = f_k(B_{k-1}, U_k)      k = 1..K
Y  = check(B_K)
f_k deterministic for code modules, the loader, splitter, parser, memory update
f_k stochastic at the model boundary, U_k the model's draw
a patch S replaces f_k by f'_k for every k in S
```

A branch the model chooses is a stochastic node whose value is the path taken. A conversation adds a time index, since the memory state of one turn enters the next. The model boundary is a draw. Its input, the prepared request, is recorded in full. Its output is not a function of that input.

### 4.3 Evidence of a pass at a boundary, claim 1

One run gives one outcome, pass or fail. The outcome is evidence about a change only when the run executed the change. One outcome is one draw from a pass probability, so a label needs enough runs to bound that probability. Three results of the structural model say where runs are needed and where they are not. They rest on the independence of mechanisms, the assumption that replacing one mechanism leaves the others as they were.

1. **Reuse of what the change does not reach.** Replacing module k leaves every state that is not downstream of k exactly as recorded. For one input only the modules after the first changed boundary need recomputation.
2. **An invariance certificate.** The patch reaches the outcome only through the boundary state it changes. When the new mechanism gives the same boundary state as the recorded one on an input, the outcome on that input is the recorded outcome. No downstream run is needed. For a code module the equality is exact. At the model boundary it is equality of the prepared request, which is exact, and equality in distribution of the reply, which needs draws. This is the one place the repetition condition enters.
3. **A reuse criterion at stochastic nodes.** The outcome under the patch is identified from recorded runs under one condition. Every stochastic module downstream of the first changed boundary receives an entering state that already appears in the records. Recorded draws then stand in for new ones. A state never seen before must be sampled. The cost of a prediction is the number of such model calls, not the length of the run.

A prediction is therefore exact computation for code modules, reuse of recorded draws where the entering state is unchanged, and fresh sampling only at changed stochastic nodes. A critic that guesses the model's reply is a fourth tier with no identification behind it.

**Estimands, per change m in context C.**

| quantity | definition | reads as |
|---|---|---|
| pass probabilities | p_C and p_{C+m} over the task set | the configuration's reliability |
| intention to treat effect | Δ = p_{C+m} − p_C | the effect of assigning the change |
| execution rate | π = P(D_m = 1 under C+m), D_m read from the probes of the modules m touches | how often the change runs |
| complier effect | Δ / π, under exclusion and monotonicity | the effect of the change when it runs |
| necessity and sufficiency | PN = Δ / p_{C+m}, PS = Δ / (1 − p_C), with the Tian and Pearl bounds without monotonicity | required in context is high PN, removable is low PN |
| sufficient set | a coherent C with p_C above the adequacy level such that every m in C has PN above the necessity level | a repair candidate |
| minimal sufficient set | a sufficient set none of whose proper subsets is sufficient, inadmissible subsets counted as not estimable | the decision object |

Pass probabilities carry Jeffreys posteriors and the labels have levels, required at P(Δ > 0) of 0.95 and removable at P(|Δ| < 0.2) of 0.95. Conditional independence of the outcome and the treatment given the boundary state does not imply that PN computed on a boundary endpoint equals PN computed on the final outcome. The displayed PN formulas also require their causal identification assumptions. The correct use of boundary information is to estimate the arm pass rates p_0 and p_1, then derive the final-outcome effect from those estimates.

### 4.4 Boundary tests as surrogates

A boundary state is a surrogate for the final outcome. The Prentice criterion asks that the outcome be independent of the treatment given the surrogate. For the full state of the changed boundary the criterion holds by the graph, because the patch has no other path to the outcome. A boundary test is a coarsening of the state, and for a coarsening the criterion holds only where it is measured. A boundary gate is reported with three properties.

- **Soundness toward the outcome.** Among recorded runs that pass the boundary test, the share whose final check passes. Among those that fail it, the share whose final check fails. Where every module downstream of the boundary is code, the test is the downstream code run on the candidate state, and soundness is exact at no model call. Where the model is downstream, the test is specified and its two shares are reported on held out inputs. A diagnostic share is also reported: among with-arm runs where the boundary did not fire, the share whose final check passed. When this share is above zero, tool invocation is shown to be insufficient as an exact substitute for the final check. Whether a richer boundary representation can still estimate the arm pass rates is a separate, open question.
- **Sensitivity.** The test fails on the buggy program and on every removal of a necessary change. This is the mutation score of the removal study.
- **Execution.** The module whose state is tested ran in that run, and the test records it.

The test at a boundary followed only by code is derived, the weakest state that makes the final check pass, obtained by executing the downstream code. The test at a boundary followed by the model is specified, as the retrieval coverage test was, and must earn its validity. The record shows why. In the 78383658 retrieval experiment all 18 R runs passed the coverage test, 12 documents retrieved and every catalog title in the request sent to the model. The published+R adventure cell still passed two of three at the end.

### 4.5 Sufficient sets over the graph, claim 2

Dependence between two changes is a graph fact. Change j and a downstream change k interact only when j's change in boundary state reaches k's entering state. When it does not, their effects separate, and j's necessity is judged without k. A change whose boundary state never differs on any input is removable with no rerun. A change whose state differs but whose downstream outcome does not needs the downstream evaluation. The minimal sufficient sets are searched over the graph, with runs spent only where states diverge. The admissibility gate of the pilot is unchanged. Its conditions are matched run conditions, intended source loaded, one declared change difference, qualified checks and coherent sides.

### 4.6 Procedure

1. Decompose the patch into changes by statement level comparison, map each change to modules through its anchors, and mark changes in scopes without a probe as not observable.
2. Run the buggy and the patched program on the frozen inputs with probes on, and read the module graph from the recorded boundary order of each run.
3. For each change and input, compare the boundary state leaving the changed module with the recorded state. Issue the invariance certificate where they are equal. Otherwise recompute the downstream code modules exactly, reuse recorded draws where the entering state of a stochastic module is recorded, and sample where it is not.
4. Allocate the samples sequentially. Each comparison keeps a posterior on Δ and on π. The next sample goes to the comparison whose decision is furthest from its level. A comparison stops when its label probability clears the level or its budget is spent. A no-op change runs beside the real changes as the negative control for resampling and pipeline nondeterminism.
5. Score every boundary test on soundness, sensitivity and execution, and report the three with the test.
6. Emit the label table. For every admissible pair, the two pass probabilities with intervals, π, Δ, the complier effect, PN and PS, and the label at the declared level and margin.
7. Enumerate the sufficient sets over the graph, mark the minimal ones, and select by the declared scope rule, module count first and change count second. Report every alternative route.

### 4.7 Contribution

The current acceptance rule is a special case of this procedure. It assumes π equal to one, fixes three repetitions in advance, reports no interval, reads only the final state and takes a single patch as the decision object. The procedure returns a label with its uncertainty and its execution rate, and closes changes at the boundary where the state is unchanged. It spends model calls only at changed stochastic nodes, reports the validity of every boundary test, and returns sets with alternatives. Module level localization, checkpoint reruns and minimal patch sets each exist in the literature. A validator that accepts a patch boundary by boundary under the execution and repetition conditions, and stops where a boundary state is unchanged, does not.

### 4.8 Evaluation

| question | measurement |
|---|---|
| Does the boundary method recover final success rates? | Error in p_0 and p_1, separately by input type and arm |
| Does it recover the repair effect? | Error in Δ_Y = p_1 minus p_0, with uncertainty |
| Does it preserve repair decisions? | False acceptance, false removal, and unresolved-decision rates |
| Does it generalize within the declared scope? | Performance on held-out inputs |
| Does it save execution? | Calls, tokens, and latency avoided after the checkpoint, minus prediction cost |
| Where is it unsupported? | Missing treatment-boundary combinations and unfamiliar boundary states |

The first question is the primary one: does the boundary method estimate arm pass rates accurately enough to support the same repair decisions as a full-execution comparison? Evaluation requires held-out inputs and a frozen boundary mapping prespecified before the held-out runs are revealed. The existing 18 runs of 77178370 establish that tool invocation is an insufficient substitute for the final check; they do not yet establish whether richer boundary information succeeds or fails as an estimator of final success rates.

## 5. Scope and limits

An environment experiment changed one input per case, the chat model, the pandas version, the embedding model and the catalog size, and reran the matched comparisons under both conditions. In the 22 comparisons that could be observed no verdict flipped. The gpt-4 condition was unresolved because the endpoint rejected every request. The three observed inputs reached no verdict's mechanism, so the environment claim stays untested. Its record is section 8 of the AgentDefect report.

The AgentIssue-Bench label harmful_edit_table means that the with side is inadequate, so it carries no survival label. The AgentIssue-Bench contrast pools the required checks of each row, the checks its verdict was computed on.

The study covers six and five cases. Each case has frozen checks, AgentDefect has no preservation check, and AgentIssue-Bench ran no repository test suite. 79343179 ran in loader scope only. The Jeffreys posterior accepts three against zero at 0.996 where Fisher gives 0.10, and both are reported.

## 6. Files and registries

| content | path |
|---|---|
| literature review | `docs/Agent_Error_Mitigation_Review (1).html` |
| AgentDefect archive numbers | `docs/agentdefect_dataset_numbers.md` |
| AgentDefect experiments, sections 1 to 9, and limitations | `motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/report.md`, `limitations.md` |
| AgentDefect records | `motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/`, `exp-2026-10-22-r/`, `exp-2026-10-23-e/`, and the reanalysis `exp-2026-10-23-v/` |
| AgentDefect number registry | `motivation_pilot/NUMBERS.md` |
| AgentIssue-Bench experiments | `/data/wang/junh/githubs/AgentIssue-Bench/motivation_experiment/exp-2026-10-21/report.md`, `exp-2026-10-22/report.md`, and the reanalysis `exp-2026-10-23-v/report.md` |
| AgentIssue-Bench number registry | `/data/wang/junh/githubs/AgentIssue-Bench/motivation_experiment/NUMBERS.md` |
| the dataset authors' result sheets | `/data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx` |
| estimator | `motivation_pilot/src/motivation_pilot/verdict_stats.py` |
| numbers of this report that appear in no other registry | `docs/NUMBERS.md` |

## Appendix A. How related work defines a module

Read on 2026-10-26 from the ModularRSI HTML, the review notes in section 6 of `docs/Agent_Error_Mitigation_Review (1).html`, the SelfHeal spreadsheet `Fix Patterns.xlsx` and the pilot code.

| source | module vocabulary | what a module is | where read |
|---|---|---|---|
| ModularRSI | Agent Loop, Observation Management, Tool Use, Context Management, Task Completion Detection. Sandbox initialization, parallel execution and LLM communication are infrastructure outside evolution | a restricted modification scope with one functional responsibility. The Agent Loop is a hub and the other four exchange inputs and outputs with it. The paper states that the arrows do not prescribe a fixed module to module execution sequence. No formal interface is defined | arXiv 2609.14857, section 3.2 and appendix B |
| HarnessFix | prompt, tool, context, orchestration and code layers | editable artifacts that runtime steps are mapped to through the paper's intermediate representation | review notes, section 6, row 1 |
| Harness-R1 | context, state, action execution, recovery | lifecycle hooks of the target runtime that a patch may edit | review notes, section 6, row 3 |
| HarnessCompass | a structural track and a guidance track. Tools, middleware, subagents, prompts, tool descriptions, skills and memory | component restricted evolution tracks whose edits are later recombined | review notes, section 6, row 4 |
| SelfHeal | Agent Core, Tools, Planning, Memory, Other, Unknown | a label per fix in the fix pattern study | `Fix Patterns.xlsx`, column Component |
| this report, dataset component table | 15 labels, among them agent_control, memory, prompt, retrieval_chain, chunking, vector_store, output_format, call_plumbing, retrieval_depth | the code area a counted change touches, one row per case | `docs/agentdefect_component_table.csv` |
| this report, pilot scopes | 14 names per case tied to line ranges, among them loader, document_splitting, vector_store, retrieval, chain_control, output_parsing | the code anchor of one declared change | `COMPONENTS` and `ANCHORS` in `motivation_pilot/src/motivation_pilot/extension.py` |
| this report, probe boundaries | memory, chat_request, network_attempt, agent_parsers, tools, embeddings, retrieval, loader | a point where the run's state is recorded | `PROBE` in the same file |
| this report, section 4.1 | a module is the code between two probe boundaries, with a functional label from the six above | a mechanism with an observable input and output state | section 4.1 |

## Appendix B. Per-input stochastic reliability, case 77178370

The 18 runs of case 77178370 split across two arms (audit\_E1, the routing repair; original, the unrepaired program) and three input types (buildings, cars, materials), with three repetitions per arm per input. The analysis below uses a Jeffreys Beta(0.5, 0.5) primary prior on each arm's pass probability and reports uniform Beta(1, 1) as sensitivity. Posterior quantities are computed from the difference distribution of independent arm draws. This analysis is retrospective; the prior was fixed after outcomes were observed. Source: `motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl`, field status, configurations audit\_E1 and original. Script: in-session Python, numpy seed 0, 500 000 samples.

**Table B1.** Arm pass rates per input type, Jeffreys primary prior.

| input | arm | passes / runs | posterior mean | 95% CrI |
|---|---|---|---|---|
| buildings | audit\_E1 (T=1) | 0 / 3 | 0.125 | \[0.003, 0.444\] |
| buildings | original (T=0) | 0 / 3 | 0.125 | \[0.003, 0.444\] |
| cars | audit\_E1 (T=1) | 3 / 3 | 0.875 | \[0.556, 0.997\] |
| cars | original (T=0) | 3 / 3 | 0.875 | \[0.556, 0.997\] |
| materials | audit\_E1 (T=1) | 3 / 3 | 0.875 | \[0.556, 0.997\] |
| materials | original (T=0) | 0 / 3 | 0.125 | \[0.003, 0.444\] |

**Table B2.** Repair effect per input type, Jeffreys primary prior. The difference ΔY = p1 − p0 is the posterior of the difference between arm pass probabilities. P(ΔY > d) reports posterior probability that the effect exceeds threshold d.

| input | E\[ΔY\] | 95% CrI | P(ΔY > 0) | P(ΔY > 0.05) | P(ΔY > 0.10) | P(ΔY > 0.20) |
|---|---|---|---|---|---|---|
| buildings | 0.000 | \[−0.444, 0.444\] | 0.500 | 0.468 | 0.434 | 0.373 |
| cars | 0.000 | \[−0.441, 0.441\] | 0.500 | 0.467 | 0.434 | 0.372 |
| materials | 0.750 | \[0.230, 0.992\] | 0.996 | 0.994 | 0.991 | 0.980 |

Uniform sensitivity for materials: E\[ΔY\] = 0.600, 95% CrI = \[0.072, 0.940\], P(ΔY > 0) = 0.986, P(ΔY > 0.20) = 0.939.

**Table B3.** Overall repair effect, stratified with equal input weights. ΔY\_overall = (ΔY\_buildings + ΔY\_cars + ΔY\_materials) / 3. Same priors as above.

| prior | E\[ΔY\_overall\] | 95% CrI | P(ΔY > 0) | P(ΔY > 0.05) | P(ΔY > 0.10) | P(ΔY > 0.20) |
|---|---|---|---|---|---|---|
| Jeffreys | 0.250 | \[−0.005, 0.481\] | 0.973 | 0.944 | 0.892 | 0.683 |
| Uniform (sensitivity) | 0.200 | \[−0.072, 0.454\] | 0.929 | 0.892 | 0.840 | 0.511 |

The three inputs carry structurally distinct information. Materials is the repair-scope input where the routing fix was designed to act; its per-input posterior gives P(ΔY > 0.10) = 0.991. Cars is a preservation check; the routing fix was not designed to change car-domain behavior, and the near-zero effect confirms it. Buildings is repair-scope but both arms fail; the routing fix executes correctly (audit\_E1 routes the buildings question to the buildings document context) yet the final check still fails, indicating a downstream failure the routing repair alone does not reach. Pooled analysis conflates all three and produces an overall CrI that crosses zero. Stratified analysis shows that sign evidence at n = 3 per arm comes entirely from materials.

The contract for case 77178370 (`motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/cases/77178370/contract.json`) labels buildings as category original and cars and materials as category related. That label does not stratify by repair-scope versus preservation-scope; it records the source of the requirement. The scope declaration used here derives from the module's postcondition: P\_core routes the entered question to the document context matching it, and this postcondition applies to buildings and materials but not to cars, whose context was never misrouted.
