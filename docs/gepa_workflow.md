# GEPA workflow

This note describes how the GEPA (Genetic-Pareto) prompt optimization method (arXiv 2507.19457) and its repository run. Repository statements cite the file and line at commit 8c7b697 of `/data/wang/junh/githubs/method-repos/GEPA`, the repository the paper links in its abstract. Paper statements cite arXiv 2507.19457v2 by section, algorithm, figure, table or appendix. Code paths are relative to `src/gepa/` in that repository, except `README.md` and `tests/`.

## 1. What the method takes as input

Paper

- GEPA receives a system Φ "instantiated with simple prompts to be optimized", a training set D_train of task instances (x, m), the evaluation metric μ, a feedback function μ_f and a total rollout budget B (§3, Algorithm 1 line 1).
- In a task instance, x maps to the input schema and m holds evaluator metadata such as gold answers, evaluation rubrics or code unit tests. The metric is `μ: Y × M → [0, 1]` (§2).
- The feedback function μ_f returns a numeric score and a feedback text with evaluation details such as compiler error messages or failed rubrics (§3, "Reflective Prompt Mutation" and "Evaluation traces as diagnostic signals").
- The hyperparameters are the minibatch size b and the Pareto set size n_pareto. D_train is split into D_feedback and D_pareto (Algorithm 1 lines 2 and 3). In the experiments the train split serves as D_feedback and the validation split as D_pareto (App. E.4).
- GEPA evolves only the prompts Π_Φ. The model weights Θ_Φ stay fixed (§3).

Code

- The entry point is `gepa.optimize` (`api.py:53`), exported at `__init__.py:8`.
- `seed_candidate` maps each component name to its text (`api.py:54`, docstring `:122`).
- `trainset` and `valset` are lists or `DataLoader` objects (`api.py:55` to `:56`). When `valset` is None, the trainset is reused as the validation set (`api.py:242`).
- The system is given as an adapter that implements `GEPAAdapter` (`api.py:57`). Its `evaluate` runs a candidate on a batch and returns per example outputs, scores and, when asked, trajectories (`core/adapter.py:163` to `:200`). Its `make_reflective_dataset` turns the trajectories into records per component, with the suggested keys "Inputs", "Generated Outputs" and "Feedback" (`core/adapter.py:203` to `:230`). The code has no separate μ and μ_f. The adapter returns both the score and the feedback text.
- Without an adapter, `task_lm` and an optional `evaluator` build a `DefaultAdapter` (`api.py:224` to `:230`). Its default evaluator `ContainsAnswerEvaluator` gives `1.0` when the gold answer string is contained in the response and returns a feedback sentence (`adapters/default_adapter/default_adapter.py:63` to `:84`).
- The budget is set by `max_metric_calls`, `stop_callbacks` or `max_reflection_cost` (`api.py:79` to `:81`). A call that yields no stopper raises an error (`api.py:314` to `:317`). The minibatch size is `reflection_minibatch_size` with a default of three (`api.py:68`, `:382`).
- A reflection LM is required unless the adapter or a custom proposer writes the new texts (`api.py:252` to `:258`).

## 2. How it proposes a change

Paper

- Each iteration selects a candidate with SelectCandidate and a module j, draws a minibatch of size b from D_feedback, runs the candidate on it and gathers feedback, scores and traces with μ_f (Algorithm 1 lines 9 to 12, §3).
- SelectCandidate builds, for every instance of D_pareto, the set of candidates with the highest score. It removes candidates "dominated by another" and samples one of the rest with probability proportional to the number of instances it leads (Algorithm 2, §3.1).
- The module to update is chosen by a "round-robin" policy (§3).
- A reflection LM is shown the current prompt, the trajectory, the score and the feedback, and proposes revised instructions (§3). The meta prompt asks it to infer the task, to include "niche and domain specific factual information" and any generalizable strategy, and to return the new instruction within triple backtick blocks (App. C).
- The new candidate is a copy of the parent with module j updated (Algorithm 1 lines 13 and 14).
- System Aware Merge takes two candidates with a common ancestor and builds a candidate from a copy of the ancestor. For each module it takes the descendant prompt that differs from the ancestor. When both differ, it takes the prompt of the descendant with the higher score (App. D.1, Algorithm 4 lines 17 to 32). Algorithm 4 contains no LM call.
- Algorithm 4 samples i and j from the whole pool and goes through their common ancestors a in turn. It skips a pair where one is an ancestor of the other, a triplet tried before, an ancestor with S[a] above min(S[i], S[j]) and a triplet that fails the Desirable check of Algorithm 3 (Algorithm 4 lines 2 to 16). The App. D.1 prose adds that merged candidates "are pareto-optimal".

Code

- With the default `SingleMutationSampling`, each iteration draws one parent from the candidate selector and one minibatch from the batch sampler (`strategies/proposal_sampling.py:52` to `:61`).
- The default selector is `ParetoCandidateSelector` (`api.py:64`, `:339`). It reads the per validation instance fronts (`core/state.py:923` to `:947`, `:1031` to `:1033`), removes candidates with `remove_dominated_programs` and samples from a list in which each candidate appears once per front it holds (`gepa_utils.py:108` to `:135`). A candidate is removed when every front that holds it still holds another remaining candidate, going from the lowest average validation score upward (`gepa_utils.py:68` to `:78`). The other selectors are `current_best`, `epsilon_greedy` and `top_k_pareto` (`api.py:338` to `:343`).
- `EpochShuffledBatchSampler` shuffles the training ids once per epoch and pads the last minibatch with the least used ids (`strategies/batch_sampler.py:26`, `:59` to `:69`).
- The parent runs on the minibatch with `capture_traces=True` (`proposer/reflective_mutation/reflective_mutation.py:283`, `:353`). When every minibatch score reaches `perfect_score=1.0`, the iteration skips reflection because `skip_perfect_score` defaults to True (`api.py:66`, `:69`, `reflective_mutation.py:451` to `:469`). This skip is not found in the paper.
- The default `module_selector` is `round_robin` (`api.py:73`). It returns one component name per iteration and advances a counter kept per candidate (`strategies/component_selector.py:10` to `:24`). A new candidate starts from the highest counter among its parents (`core/state.py:993` to `:997`).
- The adapter's `make_reflective_dataset` builds the records for the chosen component (`reflective_mutation.py:476` to `:478`). `DefaultAdapter` writes one record per minibatch example with the input, the full response and the feedback (`default_adapter.py:192` to `:197`).
- `StatelessReflectionLM` renders one prompt per component and calls the reflection LM once per prompt. When there are several prompts and the LM provides `batch_complete`, it sends them as one batch (`proposer/reflective_mutation/reflection_lm.py:142` to `:157`, `:168` to `:182`). The default template is the App. C meta prompt with `<curr_param>` and `<side_info>` placeholders (`strategies/instruction_proposal.py:148` to `:164`). When the output holds a triple backtick block, the new text is read from the outermost one (`instruction_proposal.py:88` to `:102`).
- The child copies the parent and replaces only the proposed components (`reflective_mutation.py:595` to `:598`).
- Merge is off by default (`use_merge=False`, `api.py:75`). When it is on, `MergeProposer` draws its pair from the Pareto front candidates left by `find_dominator_programs` (`proposer/merge.py:307` to `:312`, `:92`). It skips a pair where one is an ancestor of the other (`merge.py:102`). It keeps the common ancestors not yet tried with this pair, whose average validation score is not above either descendant, and that pass the component check (`merge.py:55` to `:65`, `:27` to `:43`). It picks one of them at random, weighted by average validation score (`merge.py:110` to `:116`). Each component follows the Algorithm 4 rule, with score ties broken at random (`merge.py:167` to `:197`). `merge.py` makes no LM call.

## 3. How it decides to keep or reject a change

Paper

- The new candidate is kept when its average score on the minibatch improves over the parent's average on the same minibatch (Algorithm 1 lines 15 and 16). It is then scored on every instance of D_pareto and added to the pool with its parent recorded (Algorithm 1 lines 17 to 20).
- All GEPA runs use a minibatch size of three (App. E.4).
- The validation sets hold 300 examples for HotpotQA, IFBench and HoVer and 111 for PUPA. AIME uses 90 earlier AIME questions split equally into training and validation sets. LiveBench-Math splits 368 questions equally into train, validation and test sets (App. E.1).
- Merged candidates are also evaluated "on a minibatch" first (Figure 3). The set and size of this merge minibatch are not found in the paper.
- After the budget is used, GEPA returns the candidate with the highest average score on D_pareto (Algorithm 1 line 23, §3).
- Validation scores are used only for candidate selection, and most of the rollout budget is spent on validation (§4, Observation 1). Optimizers may track validation scores, but direct access to the content of validation instances is restricted (§4).
- Merge is invoked at most five times per run when enabled (App. E.4).

Code

- The default acceptance is `strict_improvement` (`api.py:105` to `:106`). It accepts when the sum of child scores on the minibatch is strictly greater than the sum of parent scores on the same minibatch (`strategies/acceptance.py:44` to `:53`). The `improvement_or_equal` option accepts ties (`acceptance.py:56` to `:66`).
- With the default minibatch, an iteration that reflects counts three metric calls for the parent and three for the child (`reflective_mutation.py:375` to `:379`, `:648` to `:652`). An accepted child is then scored on the whole validation set (`core/engine.py:662`, `strategies/eval_policy.py:37` to `:41`), and those calls are added to the count (`engine.py:408` to `:409`). The seed is scored on the whole validation set before the loop (`engine.py:816` to `:818`, `core/state.py:1166`).
- `MaxMetricCallsStopper` stops when the count reaches `max_metric_calls` (`utils/stop_condition.py:173`). The stop check runs at the start of each iteration (`engine.py:966`).
- For each validation id the code keeps the set of candidates with the highest score, ties included (`core/state.py:932` to `:945`). The default `frontier_type` is `instance` (`api.py:65`).
- A merged candidate is scored on five validation ids, taken in equal shares from ids where the first parent scores higher, ids where the second scores higher and the remaining ids (`merge.py:266` to `:296`, `:340` to `:356`). It is kept when its sum on those ids is at least the larger of the two parents' sums (`engine.py:1031`, `merge.py:407`). A kept merge is then scored on the whole validation set (`engine.py:1033` to `:1037`).
- Each accepted reflective child adds one due merge while fewer than `max_merge_invocations` merges have been accepted (`engine.py:700` to `:703`). The default is five (`api.py:76`). A merge is tried at the start of the next iteration (`engine.py:1008` to `:1010`). Only an accepted merge raises the count (`engine.py:1039`). A rejected merge leaves it unchanged (`engine.py:1074`). An iteration that evaluates a merge skips reflective mutation (`engine.py:1072`, `:1090`).
- The returned best candidate has the highest average validation score (`core/result.py:100` to `:102`, `:310`, `core/state.py:875` to `:882`).

## 4. What it executes

Paper

- A rollout is one invocation of Φ plus its evaluation by μ (§2). In each iteration GEPA executes the selected candidate on the minibatch while tracing its execution, then evaluates the updated program on the same minibatch (§3).
- The score comes from the benchmark metric μ and the feedback text from the benchmark's feedback module (App. E.1). The HoVer feedback lists the correct documents retrieved and the documents still to be retrieved. The PUPA feedback gives the breakdown into a response quality score and a PII leakage score (App. E.1).
- In the kernel experiments the feedback function retrieves manual sections based on rollout failures such as compiler error messages, and generation runs under a cache (§5.1).

Code

- Every candidate evaluation goes through `adapter.evaluate`, called by `invoke_batch_evaluate` (`core/adapter.py:264` to `:274`). Minibatch runs request traces (`reflective_mutation.py:283`). Validation runs do not (`engine.py:332`).
- The score is the value the adapter returns. In `DefaultAdapter` the task model answers each input with the first candidate text as the system message, and `ContainsAnswerEvaluator` scores the response (`default_adapter.py:117` to `:140`).
- The paper's benchmark systems and feedback functions are not found in this repository. PUPA appears only as a test dataset (`tests/test_pareto_frontier_types/test_pareto_frontier_types.py:12`). `README.md:375` links a separate "Experiment reproduction artifact" repository.

## 5. Models by step

| step | model in the paper | model in the code | source |
|---|---|---|---|
| Run the system on the minibatch and on D_pareto | Qwen3 8B (temperature 0.6, top-p 0.95, top-k 20) or GPT-4.1 mini as `openai/gpt-4.1-mini-2025-04-14` (temperature 1.0), one model for all modules of a system, context window up to 16384 tokens | set by the adapter. With `task_lm`, `DefaultAdapter` builds `LM(task_lm)` with no temperature. README example `openai/gpt-4.1-mini` | App. E.2; `api.py:58`, `:229`; `default_adapter.py:95` to `:98`; `README.md:86` |
| Feedback function μ_f | benchmark feedback modules, no LM named | adapter code. `ContainsAnswerEvaluator` calls no model | App. E.1; `default_adapter.py:63` to `:84` |
| Candidate selection | none | none | Algorithm 2; `gepa_utils.py:108` to `:135` |
| Module selection | none ("round-robin") | none (`round_robin`) | §3; `strategies/component_selector.py:10` to `:24` |
| Reflection (UpdatePrompt) | "a reflection LM". Model not named for the §4 runs. Table 2 caption says GEPA-Qwen-Opt was "optimized entirely for (and using) the weaker Qwen3-8B". Table 4 reports reflection LM calls in columns headed GPT-4.1-Mini and Qwen3-8B. §5.1 says "we ran GEPA with GPT-4o" | `reflection_lm`, required, no default. A string becomes `LM(reflection_lm, **reflection_lm_kwargs)`. Temperature is left out of the request unless passed. README example `openai/gpt-5` | §3; Table 2; App. N Table 4; §5.1; `api.py:61` to `:62`, `:252` to `:265`; `lm.py:74`, `:86` to `:90`; `README.md:88` |
| Merge | none | none | Algorithm 4; `proposer/merge.py` |
| Accept test | none | none | Algorithm 1 line 16; `strategies/acceptance.py:50` to `:53` |

How the code calls its model

- `gepa.lm.LM` wraps LiteLLM. A single call goes through `litellm.completion` with `num_retries=3` and `drop_params=True` (`lm.py:76`, `:115` to `:129`). A batch goes through `litellm.batch_completion` with `max_workers=10` by default (`lm.py:153` to `:178`).
- `DefaultAdapter` sends the task requests through `LM.batch_complete` with `max_litellm_workers=10` (`default_adapter.py:92`, `:131` to `:134`). When the task model is a callable instead of a string, the callable is called once per input (`default_adapter.py:135` to `:137`).
- A callable passed as `reflection_lm` is called directly. It is wrapped in `TrackingLM` for token estimates unless it already exposes `total_cost` (`api.py:266` to `:271`, `lm.py:213` to `:259`).
- `LM` sets no endpoint, base URL or key. Extra keyword arguments such as `api_key` and `api_base` pass through to LiteLLM (`lm.py:67` to `:68`, `:89`, `:128`). For the reflection LM they come from `reflection_lm_kwargs` (`api.py:265`). `gepa.optimize` builds `DefaultAdapter` from `task_lm` and `evaluator` only (`api.py:229`). Where a key is read when none is passed is not found in `lm.py` or `api.py`.

## 6. Embedding model

- An embedding model is not found in the paper.
- The optimization loop in `api.py`, `core/`, `proposer/` and `strategies/` calls no embedding model.
- Embedding models appear only in the optional RAG adapter and its example. `GenericRAGAdapter` defaults `embedding_model` to `text-embedding-3-small` (`adapters/generic_rag_adapter/generic_rag_adapter.py:152`), and its default embedding function calls `litellm.embedding` with it (`adapters/generic_rag_adapter/rag_pipeline.py:226` to `:232`). The RAG example uses `SentenceTransformer("all-MiniLM-L6-v2")` and falls back to `ollama/nomic-embed-text:latest` (`examples/rag_adapter/rag_optimization.py:169`, `:178`).

## 7. How the paper scores the method

- The benchmarks are HotpotQA, IFBench, HoVer, PUPA, AIME-2025 and LiveBench-Math, each paired with a compound AI system and a feedback function (§4, App. E.1). The systems run on Qwen3 8B and on GPT-4.1 mini, named `openai/gpt-4.1-mini-2025-04-14` in App. E.2 (§4, App. E.2).
- Each benchmark has a train, validation and test split. Optimizers have full access to the train split with labels. Tables 1 and 2 report test set scores (Table 1 caption, App. F). The AIME-2025 test set has 30 questions. Each question is repeated five times (App. E.1).
- Tables 1 and 2 give per benchmark scores, an "Aggregate" column and an "Improvement" column over the Baseline, which is the base program without optimization (App. E.4). The comparators are MIPROv2, GRPO with 24,000 rollouts, Trace with OptoPrime and TextGrad (§4, Tables 1 and 2, App. E.4). GEPA's rollout budget per benchmark is capped at the number of rollouts MIPROv2 used, and Table 1 lists it (App. E.4, Table 1).
- §2 names exact match, F1 and pass rate as example metrics. App. E.1 describes HoVer evaluation as retrieving all gold documents and the PUPA score as an aggregate of a response quality score and a PII leakage score. The abstract reports AIME-2025 gains as accuracy. A metric definition for HotpotQA, IFBench and LiveBench-Math is not found in the paper.
- Table 3 compares candidate selection strategies (SelectBestCandidate, BeamSearch and GEPA) with Qwen3 8B (§4, Observation 3). Figures 1 and 12 to 15 plot score against rollouts (Figure 1, App. G). Figure 16 shows the generalization gap (App. H). Figures 17 and 18 compare prompt lengths (App. I). Table 4 counts reflection LM calls (App. N).
- §5.1 scores kernel generation by mean vector utilization on NPUEval and by fast_p on 35 KernelBench tasks (§5.1, Figures 7 and 8). §5.2 scores adversarial prompt search by pass@1 on AIME-2025 with GPT-5 Mini and five runs per problem (§5.2).
