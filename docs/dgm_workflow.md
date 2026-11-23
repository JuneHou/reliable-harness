# DGM workflow

This note describes how the DGM (Darwin Gödel Machine) method (arXiv 2505.22954) and its repository run. A repository statement cites the file and line at commit a565fd2 of `/data/wang/junh/githubs/method-repos/DGM`, whose remote is `https://github.com/jennyzzt/dgm`, the code link in the paper abstract. A paper statement cites the section, table or appendix of arXiv 2505.22954v3.

## 1. Input

- The DGM takes an initial coding agent, a benchmark suite and a maximum number of iterations (App. C.4, Algorithm 1).
- In the paper the initial agent is built around a frozen FM with two tools, a Bash tool and an edit tool (§4.1, App. C.1). It receives one prompt with the repository location, the problem statement and the repository's testing framework (§4.1, App. C.1).
- The code entry point is `main` in `DGM_outer.py:221`, run as `python DGM_outer.py` (`README.md:67`).
- The initial SWE-bench agent is the class `AgenticSystem` (`coding_agent.py:67`). Its `forward` sends the task prompt to `chat_with_agent` (`coding_agent.py:153` to `:169`). The class also defines `get_regression_tests` and `run_regression_tests`, and `forward` calls neither (`coding_agent.py:98` to `:151`).
- The tools are the modules in `tools/` (`tools/__init__.py:4` to `:31`). They are `bash` (`tools/bash.py:6`) and `editor` with the commands `view`, `create` and `edit` (`tools/edit.py:6`, `:19`).
- The initial Polyglot agent is `coding_agent_polyglot.py` (`coding_agent_polyglot.py:96`). In a Polyglot run the self-modification container renames it to `coding_agent.py` (`self_improve_step.py:276` to `:282`). Its task prompt has no `<test_description>` block (`coding_agent_polyglot.py:144` to `:152`). The task prompt in the paper has one (App. C.1).
- Algorithm 1 evaluates the base agent before the first iteration (App. C.4). The code starts the archive as `['initial']` (`DGM_outer.py:19`) and copies stored results of the base agent from `initial/` or `initial_polyglot/` into the run folder (`DGM_outer.py:27` to `:33`). The base agent is not evaluated inside the loop (`DGM_outer.py:254` to `:332`).
- `initial/metadata.json` records an `accuracy_score` of 0.2 with 12 of 60 SWE-bench tasks resolved (`initial/metadata.json:4` to `:6`). `initial_polyglot/metadata.json` records 0.142 with 32 of 225 Polyglot tasks resolved (`initial_polyglot/metadata.json:4` to `:6`).
- The benchmarks are SWE-bench Verified and Polyglot (§4.2). The code loads `princeton-nlp/SWE-bench_Verified` (`self_improve_step.py:246`, `swe_bench/harness.py:206`). It reads Polyglot from `polyglot/polyglot_benchmark_metadata.json` (`self_improve_step.py:242`). `polyglot/prepare_polyglot_dataset.py` writes that file from a clone of `Aider-AI/polyglot-benchmark` (`polyglot/prepare_polyglot_dataset.py:238`, `:249`).
- The loop reads the first and second task lists of the chosen benchmark (`DGM_outer.py:257` to `:262`).
- `swe_bench/subsets/small.json` holds ten task IDs. `swe_bench/subsets/medium.json` holds 50. `swe_bench/subsets/big.json` holds 140. These are the same task IDs as the three lists in App. E.2.
- `polyglot/subsets/small.json` holds ten task IDs. `polyglot/subsets/medium.json` holds 50. These are the same task IDs as the two lists in App. E.3.

## 2. Proposing a change

- The paper runs the DGM for 80 iterations (§4.1). It generates one new agent per iteration and runs two iterations in parallel for SWE-bench and four for Polyglot (§4.1). App. C.2 says `k` parents are drawn in each iteration, with `k = 2` for SWE-bench and `k = 4` for Polyglot.
- The code runs `max_generation` generations with default `80` (`DGM_outer.py:223`, `:270`). Each generation starts `selfimprove_size` attempts with default `2` on `selfimprove_workers` threads with default `2` (`DGM_outer.py:224` to `:225`, `:282` to `:300`). A search of the repository finds `selfimprove_size` only in `DGM_outer.py`, so no Polyglot value is set in the code (`DGM_outer.py:224`).

### Parent selection

- In the DGM, parent selection is "roughly proportional to each agent's performance score and inversely proportional to the number of its children with codebase-editing functionality" (§3).
- App. C.2 defines an eligible set of archive agents whose score `α_i < 1`. It sets `s_i = 1 / (1 + exp(-λ(α_i - α_0)))` with `λ = 10` and `α_0 = 0.5`, `h_i = 1 / (1 + n_i)` with `n_i` the number of functioning children, `w_i = s_i h_i` and `p_i = w_i / Σ_j w_j`. It draws `k` parents with replacement from the eligible set (App. C.2).
- The code default is `score_child_prop` (`DGM_outer.py:227`). It computes `1 / (1 + math.exp(-10*(score-0.5)))` times `1 / (1 + count)`, normalizes and calls `random.choices(commits, probabilities, k=selfimprove_size)` (`DGM_outer.py:91` to `:100`).
- The score is `overall_performance.accuracy_score` in each archive member's `metadata.json` (`DGM_outer.py:58` to `:68`). The children count is the number of archive members whose `parent_commit` is that agent (`DGM_outer.py:69` to `:72`).
- The candidate set is every archive member whose metadata loads, with no condition on the score (`DGM_outer.py:57` to `:76`). The eligible set of the paper leaves out agents with a perfect score (App. C.2).

### Task whose log is diagnosed

- The paper does not say how the task whose log is diagnosed is chosen (App. C.3).
- For SWE-bench the code picks one entry per parent (`DGM_outer.py:121` to `:148`). When empty patches make up at least 10% of the parent's evaluated tasks, it picks `solve_empty_patches` with probability 0.25 (`DGM_outer.py:124` to `:128`). Otherwise it picks `solve_stochasticity` with probability 0.25 (`DGM_outer.py:130` to `:134`). Otherwise, when the log of an empty or unresolved task shows the error `Input is too long for requested model` twice in a row, it picks `solve_contextlength` with probability 0.25 (`DGM_outer.py:37` to `:48`, `:136` to `:141`). Otherwise it picks a random unresolved task (`DGM_outer.py:143` to `:148`).
- For Polyglot the code picks a random task among the parent's empty and unresolved tasks, or among all its tasks when there are none (`DGM_outer.py:117` to `:120`, `:147`).

### Diagnosis

- §3 says each selected parent analyzes its own benchmark evaluation logs and proposes the next feature to implement. App. C.3 says the current implementation uses a separate FM, OpenAI's o1, to diagnose improvement opportunities from the evaluation logs of the chosen agent. App. C.3 says `implementation_suggestion` and `problem_description` are extracted from the diagnosis and passed to the coding agent as its self-modification task.
- In the code, `diagnose_problem` in `self_improve_step.py` calls the model set in `diagnose_model` before the coding agent runs (`self_improve_step.py:28`, `:30` to `:67`, `:315` to `:319`). This call is not part of the agent's code (`self_improve_step.py:30` to `:67`).
- The system message holds a fixed summary of the agent and the agent's code (`prompts/self_improvement_prompt.py:326` to `:334`). The code is `coding_agent.py` and the `.py` files under `tools/` and `utils/` of the repository root, minus the files in `exclude_files`, followed by the text of every patch in the parent's lineage (`prompts/self_improvement_prompt.py:326` to `:333`, `:409` to `:468`).
- For an ordinary SWE-bench task the user message holds the agent's log for that task, the issue text, the predicted patch, the SWE-bench test patch and the test results (`prompts/self_improvement_prompt.py:77` to `:120`, `:317` to `:323`). Only the first log found is used, and it is clipped at 250000 characters (`prompts/self_improvement_prompt.py:242` to `:249`). The gold patch `answer_patch` is passed to `format`, and the template has no field for it (`prompts/self_improvement_prompt.py:77` to `:120`, `:323`).
- For `solve_empty_patches`, `solve_stochasticity` and `solve_contextlength` the user message is a fixed prompt with no task log (`prompts/self_improvement_prompt.py:122` to `:172`, `:305` to `:314`).
- For Polyglot, with probability 0.25 the user message is a fixed prompt on stochasticity with the task log (`prompts/self_improvement_prompt.py:362` to `:364`). Otherwise a task with an empty patch gets a fixed empty patch prompt with the log (`prompts/self_improvement_prompt.py:365` to `:367`). Otherwise the general prompt is used, with the task's reference tests in the test patch field (`prompts/self_improvement_prompt.py:346` to `:348`, `:368`).
- The reply is parsed for a JSON block (`self_improve_step.py:52`, `llm.py:305` to `:359`). On failure the call is retried up to three times (`self_improve_step.py:30`, `:55` to `:66`).
- The problem statement given to the coding agent is the fixed agent summary followed by `# To Implement`, `implementation_suggestion` and `problem_description` (`prompts/self_improvement_prompt.py:174` to `:181`). Without a problem statement the attempt ends with no child (`self_improve_step.py:328` to `:333`).
- A second diagnosis of the child after its evaluation runs only with `--post_improve_diagnose`, which is off by default (`DGM_outer.py:235`, `self_improve_step.py:401` to `:416`).

### Self-modification

- In the DGM the parent implements the suggested feature into its own codebase and so generates a new coding agent (§3). Algorithm 1 writes this step as `c ← p.modify(p)` (App. C.4).
- The code starts one Docker container per attempt from the image `dgm` (`self_improve_step.py:263` to `:274`). The image is built from the repository `Dockerfile`, which copies the whole repository into `/dgm` (`utils/docker_utils.py:118`, `Dockerfile:11`, `:14`).
- It applies every `model_patch.diff` of the parent's lineage, oldest first (`utils/evo_utils.py:28` to `:41`, `self_improve_step.py:292` to `:300`). It commits the result and reinstalls `requirements.txt` (`self_improve_step.py:302` to `:313`).
- It runs `python /dgm/coding_agent.py --self_improve` with `--git_dir /dgm/` and the problem statement (`self_improve_step.py:347` to `:358`). The test description tells the agent to run `cd /dgm/ && pytest -rA <specific test files>`, to test only tools and utils and never to run `agentic_system.forward()` (`self_improve_step.py:338`, `prompts/testrepo_prompt.py:27` to `:28`).
- The agent works on `/dgm` through its `bash` and `editor` tools until the model makes no further tool call (`llm_withtools.py:363` to `:408` for Claude, `:453` to `:502` for o3-mini).
- The diff of `/dgm` against the commit becomes the child's `model_patch.diff` (`coding_agent.py:197` to `:201`, `self_improve_step.py:361` to `:365`). A missing or empty patch ends the attempt before evaluation (`self_improve_step.py:367` to `:379`).
- The editing model is `CLAUDE_MODEL` for SWE-bench (`coding_agent.py:85`). For Polyglot it is `OPENAI_MODEL`, because `--self_improve` is set (`coding_agent_polyglot.py:116`, `self_improve_step.py:356`). Section 5 compares this with the paper.

## 3. Keeping or rejecting a change

- In the DGM only agents that "compile successfully and retain the ability to edit a given codebase" are added to the archive, and all others are discarded (§3). Algorithm 1 adds a child when `c.is_valid()` holds (App. C.4).
- In the code, `filter_compiled` keeps a child when `is_compiled_self_improve` returns true (`DGM_outer.py:152` to `:165`, `:317` to `:321`, `utils/evo_utils.py:96` to `:127`).
- `is_compiled_self_improve` requires that `overall_performance` holds `accuracy_score`, `total_unresolved_ids`, `total_resolved_ids` and `total_emptypatch_ids` (`utils/evo_utils.py:106` to `:112`). It requires at least one task with a resolved or unresolved result, which means at least one non-empty patch (`utils/evo_utils.py:114` to `:119`). It requires `total_submitted_instances` to be at least the length of the first task list (`utils/evo_utils.py:121` to `:125`, `DGM_outer.py:320`).
- With the default `keep_all` every child that passes is added to the archive (`DGM_outer.py:186` to `:188`, `:232`). The default rule compares no score with the parent or with the base agent (`DGM_outer.py:174` to `:190`).
- With the option `keep_better` a child is added only when its score is at least the base agent's score minus `eval_noise`, default `0.1` (`DGM_outer.py:178` to `:185`, `:238`).
- The loop collects each finished attempt with `future.result(timeout=1.5*60*60)`, and an attempt that raises an exception adds no child (`DGM_outer.py:302` to `:313`).

### Staged evaluation

- The paper first evaluates each agent on ten tasks "to verify basic codebase-editing functionality" (§4.2). Agents that pass this stage are evaluated on an expanded set of 50 tasks (§4.2). The paper gives no numeric rule for passing the first SWE-bench stage (§4.2).
- For SWE-bench, an agent with over 40% success on the 60-task subset that ranks among the top two in the archive is evaluated on 200 tasks, 140 plus the previous 60 (§4.2, App. E.2).
- For Polyglot, an agent with over 40% success on the ten-task subset is evaluated on the 50-task subset (§4.2, App. E.3).
- In the code the first stage runs the child on `small.json` (`DGM_outer.py:292`, `self_improve_step.py:127` to `:137`, `:182` to `:194`).
- The second stage runs `medium.json` when `total_resolved_instances >= len(test_task_list) * test_more_threshold` with `test_more_threshold = 0.4` (`DGM_outer.py:268`, `:293` to `:294`, `self_improve_step.py:153` to `:166`, `:202` to `:216`). The rule is the same for both benchmarks (`self_improve_step.py:155`, `:204`). The paper says "over 40%" (§4.2), and the code uses "at least" (`self_improve_step.py:155`, `:204`).
- For the third stage, `get_full_eval_threshold` takes the second highest score among the base agent and the archive members evaluated on at least 90% of the tasks in all three lists, and raises it to `0.4` when lower (`DGM_outer.py:192` to `:219`). The loop passes it to `self_improve` as `full_eval_threshold` (`DGM_outer.py:296`).
- `self_improve_step.py:234` is the only line of that file that names `full_eval_threshold`. `self_improve_step.py:258` loads `big.json` into `test_task_list_big`, and no other line of the file names it. The 140-task list runs only through the separate script `test_swebench.py` with `--test_big` (`test_swebench.py:22`, `:38` to `:40`).
- For SWE-bench the second stage replaces `overall_performance` (`self_improve_step.py:176` to `:177`). `get_all_performance` sums resolved and submitted counts over every report file in the attempt folder whose name contains the run ID (`utils/evo_utils.py:54` to `:57`, `:71` to `:86`).
- For Polyglot the second stage result is stored as `overall_performance_deep` (`self_improve_step.py:219` to `:220`). Parent selection and archive admission read `overall_performance` (`DGM_outer.py:63`, `utils/evo_utils.py:106`).

### Runs per task

- The code runs each task once per stage, because `num_swe_evals` defaults to `1` (`DGM_outer.py:234`, `:289`, `swe_bench/harness.py:254` to `:255`). The Polyglot harness raises an error when `num_evals > 1` (`polyglot/harness.py:269` to `:270`).
- The paper reports pass@1 for Polyglot, where the agent never sees ground-truth test results (§4.2, App. E.5). A repeat count per SWE-bench task is not found in the paper.

## 4. What runs

- The DGM runs every new agent on benchmark tasks inside the loop (§3, `self_improve_step.py:386` to `:399`). The parent is not run again, and the diagnosis reads the stored logs of the parent's earlier evaluation (`prompts/self_improvement_prompt.py:200` to `:208`).
- The paper says all agent execution and self-modification run in isolated sandboxed environments, each under a strict time limit (§5). The paper says agents ran in isolated sandboxes with strict resource and time limits and had limited network access (Ethics Statement).
- The self-modification container uses the base image `python:3.10-slim` (`Dockerfile:2`). It is started with `client.containers.run(image=image_name, name=container_name, detach=True)` and no network or resource argument (`utils/docker_utils.py:133`). The agent runs under `timeout 1800` (`self_improve_step.py:348`). The `bash` tool stops a command after 120 seconds (`tools/bash.py:33`).
- For SWE-bench each task runs in a container built by `build_container` of the `swebench` package (`swe_bench/harness.py:12`, `:53`). That package is cloned from the SWE-bench repository at commit `dc4c087c2b9e4cefebf2e3d201d27e36` and is not part of this repository (`README.md:52` to `:57`).
- The SWE-bench harness copies the agent files into `/dgm`, applies the lineage patches and runs the agent on `/testbed/` under `timeout 32400` (`swe_bench/harness.py:74` to `:82`, `:99` to `:106`, `:123` to `:134`). Tasks run with `max_workers=min(5, len(test_task_list))` (`self_improve_step.py:131`).
- For Polyglot each task runs in a container created with `nano_cpus` from the language settings and no network argument (`polyglot/docker_build.py:529`, `:533` to `:541`). The agent runs under `timeout 600` (`polyglot/harness.py:112`).
- The agent process runs inside the containers, so its model calls start there (`self_improve_step.py:358`, `swe_bench/harness.py:134`, `polyglot/harness.py:122`). The host passes `ANTHROPIC_API_KEY`, `AWS_REGION`, `AWS_REGION_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `OPENAI_API_KEY` into each container (`self_improve_step.py:339` to `:346`, `:358`, `swe_bench/harness.py:114` to `:121`, `:134`, `polyglot/harness.py:102` to `:109`, `:122`).

### Evaluator

- The paper uses "SWE-bench's official private tests" to detect whether an issue is solved (App. C.3).
- The SWE-bench harness reads `/dgm/model_patch.diff` from the task container (`swe_bench/harness.py:147` to `:151`). Diff blocks for test paths are removed (`swe_bench/report.py:37` to `:65`, `:77`). The SWE-bench script `swebench/harness/run_evaluation.py` then runs as a subprocess and decides pass or fail (`swe_bench/report.py:83` to `:93`). Its code is not in this repository (`README.md:52` to `:57`).
- For Polyglot the harness decides pass or fail itself (`polyglot/harness.py:145` to `:188`). An empty patch is recorded as `empty_patch` (`polyglot/harness.py:147` to `:158`). Otherwise the harness stashes the solution files, resets the task repository to `test_commit`, cleans it and restores the stash (`polyglot/harness.py:161` to `:168`). The dataset script sets `test_commit` from `all_files_commit` and `base_commit` from `solution_commit` (`polyglot/prepare_polyglot_dataset.py:75` to `:77`).
- The harness then runs the language's test command under `timeout 120` (`polyglot/harness.py:170` to `:182`). Exit code 0 gives `resolved`, and any other exit code gives `unresolved` (`polyglot/harness.py:185` to `:188`).

## 5. Models by step

The DGM steps and their models are listed below. Model IDs are named by the variable that holds them, and the exact strings are at the cited lines.

| step | model in the paper | model in the code | source |
|---|---|---|---|
| Diagnosis of the parent's failed task | OpenAI o1 (App. C.3) | `o1-2024-12-17` in `diagnose_model`, called with `temperature=1`, `n=1`, `seed=0`, no token limit | `self_improve_step.py:28`, `llm.py:231` to `:244` |
| Self-modification, SWE-bench | Claude 3.5 Sonnet (New) (§4.1, Table 3) | `bedrock/us.anthropic.claude-3-5-sonnet-20241022-v2:0` in `CLAUDE_MODEL`, called with `max_tokens=4096` and no temperature argument | `coding_agent.py:85`, `llm_withtools.py:13`, `:36` to `:43` |
| Self-modification, Polyglot | Claude 3.5 Sonnet (New) (Table 3) | `o3-mini-2025-01-31` in `OPENAI_MODEL`, selected because `--self_improve` is set, called with no temperature argument | `coding_agent_polyglot.py:116`, `self_improve_step.py:356`, `llm_withtools.py:14`, `:44` to `:51` |
| Benchmark evaluation, SWE-bench | Claude 3.5 Sonnet (New) (§4.1, Table 3) | `CLAUDE_MODEL` as above | `coding_agent.py:85`, `swe_bench/harness.py:123` to `:133` |
| Benchmark evaluation, Polyglot | o3-mini (§4.1, Table 3) | `CLAUDE_MODEL`, selected because the harness does not pass `--self_improve` | `coding_agent_polyglot.py:116`, `polyglot/harness.py:111` to `:121` |
| Diagnosis of the child after evaluation | not found in the paper | `o1-2024-12-17` in `diagnose_model`, run only with `--post_improve_diagnose` (off by default) | `self_improve_step.py:89`, `:402` to `:416`, `DGM_outer.py:235` |
| Temperature | 1.0 for all FMs in every setting (App. D.1) | `temperature=1` in the o1 call. The Claude and o3-mini tool calls pass none. `get_response_from_llm` has default `temperature=0.7`, and its o1 branch passes `1` | `llm.py:179`, `:239`, `llm_withtools.py:37` to `:51` |

### How the code calls its models

- The client libraries are `anthropic` and `openai` (`requirements.txt:2` to `:3`, `:7`). `create_client` picks the client from the model ID (`llm.py:44` to `:85`).
- For a `bedrock/` Claude ID it builds `anthropic.AnthropicBedrock` with `aws_access_key`, `aws_secret_key` and `aws_region` read from `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_REGION_NAME` (`llm.py:55` to `:63`).
- For an o1 or o3 ID it builds `openai.OpenAI()` with no argument, so the code passes it no base URL and no key (`llm.py:68` to `:70`). No base URL is passed to `anthropic.AnthropicBedrock` (`llm.py:58` to `:62`). Base URLs appear only in the DeepSeek and OpenRouter branches (`llm.py:71` to `:83`).
- The README asks the user to export `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` (`README.md:27` to `:28`).
- The coding agent calls Claude with `client.messages.create` and its tools with `tool_choice` set to auto (`llm_withtools.py:37` to `:43`, `:369` to `:376`). It calls o3-mini with `client.responses.create` and `parallel_tool_calls=False` (`llm_withtools.py:45` to `:51`). Rate limit, timeout and status errors are retried with exponential backoff (`llm_withtools.py:25` to `:30`).
- The diagnosis calls o1 with `client.chat.completions.create`, with the system message placed in front of the user message (`llm.py:231` to `:244`).

## 6. Embedding model

- The DGM paper names no embedding model. The paper text, appendices included, contains no occurrence of the string "embed" (arXiv 2505.22954v3, full text).
- The code uses no embedding model. No file outside the stored run outputs in `initial/`, `initial_polyglot/` and `swe_bench/ref_agent_results/` contains the string "embed" (repository search at commit a565fd2).

## 7. Scoring

- The paper scores the DGM by the percentage of solved tasks on the benchmark subsets of §4.2 (§4.3, §4.4, Figure 2). On Polyglot it reports pass@1 (§4.2, App. E.5). SWE-bench means SWE-bench Verified throughout the paper (§4.2).
- After 80 iterations the score rises from 20.0% to 50.0% on SWE-bench and from 14.0% to 38.0% on Polyglot (§4.4, Figure 2). On the full Polyglot benchmark the base agent scores 14.2% and the best discovered agent 30.7% (§4.4).
- The baselines are DGM w/o self-improve and DGM w/o open-ended exploration (§4.3, App. C.4 Algorithms 2 and 3) and DGM Greedy (App. A.3). Table 1 gives the scores of DGM and these three on both benchmarks (App. A.3).
- The handcrafted comparisons are OpenHands + CodeAct v2.1 on the same 200 SWE-bench tasks, at 51.0% (App. E.4), and Aider on Polyglot (§4.3, App. E.5). They are shown as dotted lines in Figure 2 (§4.3).
- Transfer across models, benchmarks and programming languages is reported in §4.4, Figure 4 and App. A.2. Table 2 gives the percentage of generated agents with basic code-editing functionality on SWE-bench (App. A.4). App. A.4 reports three DGM runs on Polyglot.
