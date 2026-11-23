# RRSI workflow

This note describes how the RRSI regularized recursive self-improvement method (arXiv 2609.24972) and its repository run. A repository statement cites the file and line at commit be50316 of `/data/wang/junh/githubs/method-repos/RRSI`, the repository the paper links (Abstract). A paper statement cites the section, equation, table, algorithm line or appendix.

## 1. What the method takes as input

- The paper treats an agent as a frozen backbone policy plus a harness. The harness holds the system and task prompts, the control flow, the tool interfaces, the memory and skill files and the context management (§2).
- Each task comes with its environment. A verifier scores the trajectory in `[0, 1]`. The verifier can be a unit test suite or an LLM judge program (§2).
- The search starts from an initial harness `H_0` and uses a fixed evolve set `D_evolve` (§2, App. D.1). The edit space stays open. Prompts, control flow, configuration, context management, tools, skills, memory and subagents may all be modified, added or removed (§3.1).
- The evolve sets are Terminal-Bench 2.1 with 89 tasks, Harvey LAB with a 120 task evolve split and a 40 task held-out split, and EngDesign with 61 tasks and no held-out split (§4.1, App. B.3, App. B.7).
- The code entry point is `main` at `rrsi.py:65`. It loads the domain adapter, reads the hyperparameters from `domains/<domain>/rrsi.json` and builds the run (`rrsi.py:95` to `:98`). One round is `Run.round` (`rrsi/loop.py:231`).
- The domain adapter supplies the task splits, the runner and scorer, trace loading and rendering, the liveness check, the leakage denylist, the diff signals for component tags, the role texts and the acceptance guards (`rrsi/domain.py:28` to `:43`). It also names the evolvable directory `harness_path` and the proposer's `SKILL.md` and `PATTERNS.md` (`rrsi/domain.py:57`, `:109` to `:111`).
- The evolvable directories are `third_party/harbor_terminus2` for coding (`domains/coding/adapter.py:108`), `third_party/archipelago/harness_workspace` for Harvey LAB (`domains/workspace/adapter.py:94`) and `third_party/archipelago/harness_eng` for EngDesign (`domains/eng/adapter.py:78`).
- `H_0` is the tip of the git branch `evolve/<domain>` (`rrsi/loop.py:88`, `:181` to `:184`).
- Coding evolves on the 89 task names in `domains/coding/data/tb21_tasks.txt` (`domains/coding/adapter.py:137` to `:145`). EngDesign evolves on the 61 tasks in `domains/eng/data/split_engd.json` (`domains/eng/adapter.py:117` to `:118`).
- The Harvey LAB split is generated from a Harvey LAB checkout on first use (`domains/workspace/adapter.py:63` to `:73`). The generator keeps tasks with at most 100 criteria and at most 20MB of documents. It picks 120 evolve tasks and 40 held-out tasks stratified by practice area (`domains/workspace/split_workspace.py:40` to `:47`, `:59` to `:61`).

## 2. How it proposes a change

A round is Algorithm 1 followed by Algorithm 2 (App. D.1). The code follows the same order (`rrsi/loop.py:28` to `:42`).

### Step 1. Analysis

- Paper. `F_t = Analyze(H_t, D_evolve)` gives the failure feedback of the incumbent (App. D.1, Alg. 1 line 3). The analyst writes the cross-round failure feedback and is Claude Opus 4.8 (§4.1).
- Code. The analyst reads traces from the stored evaluation of the incumbent and does not run it again (`rrsi/loop.py:245`, `:250`). It takes the worst trial of the lowest scoring tasks and the best trial of the highest scoring tasks (`rrsi/loop.py:134` to `:150`).
- The number of lowest scoring tasks is 30 for coding, 60 for Harvey LAB and 22 for EngDesign (`domains/coding/rrsi.json:20`, `domains/workspace/rrsi.json:10`, `domains/eng/rrsi.json:20`). The number of highest scoring tasks is six in each instance (`domains/coding/rrsi.json:21`, `domains/workspace/rrsi.json:10`, `domains/eng/rrsi.json:21`).
- The analyst does not read traces itself. It sends up to eight requests per call to digester subagents. Each digester reads one rendered trace with read-only tools (`rrsi/analyst.py:59` to `:73`, `:166`, `rrsi/digester.py:28` to `:34`, `:51` to `:54`).
- The analyst returns a report with `failure_modes`, `capability_gaps` and `success_habits` (`rrsi/analyst.py:28` to `:38`, `:159` to `:164`). Mode and habit names carry over to the next round through `global_analysis.json` (`rrsi/loop.py:258` to `:267`).
- The digester role and the three report fields are not found in the paper.

### Step 2. Budget, stall flag and prune set

- Paper. The edit budget `b_t = ceil(b_min + (b_max - b_min) * (1 + cos(pi t / T)) / 2)` caps the number of independently attributable edits in one candidate (§3.2, Eq. 4).
- Paper. The stall flag is `sigma_t = 1[S_t - S_{t-w} <= delta]` and the untried components are `U_t = K \ T_t` (App. D.2, Eq. 13). The prune set is `B_t = {l in T_t : g_t(l) <= 0}`, where `g_t(l)` is the best measured gain of component `l` within the last `n_prune` rounds (App. D.2, Eq. 11, Eq. 14).
- Code. `edit_budget` computes Eq. 4 (`rrsi/schedule.py:140` to `:147`). `History.prune_set`, `stall_flag` and `exploration` compute the other three (`rrsi/history.py:152` to `:163`, `:189` to `:211`). The round calls them at `rrsi/loop.py:274` to `:279`.
- The component vocabulary `K` holds the nine tags of Eq. 12 (`rrsi/components.py:44` to `:46`, App. D.2).

### Step 3. Proposer

- Paper. The proposer draws candidates from `P_reg(. | H_t, F_t, L_t, b_t, E_t, B_t)` and tags each atomic edit with a component and a hypothesis (App. D.1, Alg. 1 lines 10 and 11). It conditions on the edit history, which records the component, the hypothesis, the source diff, the score change, the cost change and the acceptance of every evaluated candidate (§3.2, App. D.2 Eq. 10). The proposer is Claude Opus 4.8 (§4.1).
- Code. Each round drafts `m` candidates. Each one lives in its own git worktree on the branch `<domain>/r<t><variant>` (`rrsi/loop.py:292` to `:297`, `:458` to `:459`, `:474`). `m` is two in every shipped `rrsi.json` (`domains/coding/rrsi.json:5`, `domains/workspace/rrsi.json:3`, `domains/eng/rrsi.json:5`).
- The proposer is an agent loop of at most 40 turns that replies with one JSON action per turn (`rrsi/propose.py:56`, `:307`). The actions list files, read a file, list traces, read a rendered trace, edit a file, write a new file and call `done` (`rrsi/propose.py:71` to `:105`).
- It reads the edit history, an attribution scoreboard of past predictions, the exploration directives, the prune set, the analysis report, the per task digests, the full current harness source and the budget (`rrsi/propose.py:264` to `:304`). `SKILL.md` and `PATTERNS.md` go in as a cached prefix (`rrsi/propose.py:253` to `:256`, `:311` to `:312`). The scoreboard, `SKILL.md` and `PATTERNS.md` are not found in the paper.
- The proposer sees the most recent 40 history records (`rrsi/history.py:166`, `rrsi/loop.py:280`). At most four of them are records without a measurement (`rrsi/history.py:171` to `:180`). The rendered records leave out the diff (`rrsi/history.py:181` to `:185`). The paper describes credit assigned over the full evolution history (§5).
- It edits files only inside the harness directory of the domain (`rrsi/propose.py:147` to `:155`). `write_file` creates new files only (`rrsi/propose.py:179` to `:187`).
- `done` is refused while the declared edits exceed `b_t`, while an edit lacks its tags, or while a reserved exploration slot holds no edit on an untried component (`rrsi/propose.py:338` to `:359`). The reserved slots go to the last `m_draft` variants when the stall flag is set and untried components remain (`rrsi/loop.py:294`).
- The paper puts the pool the proposer drafts from at 80 edits (App. E.1). In the code `MAX_EDITS = 80` caps the successful `edit_file` and `write_file` actions of one proposer run (`rrsi/propose.py:57`, `:392` to `:402`).

### Step 4. Leakage critic

- Paper. Before evaluation a critic reads each candidate diff. It rejects edits that encode task names, entity names, task specific values, answers or other logic specific to the evolve benchmark, and edits that add inert machinery (§3.3). The critic reads the diff, not the proposal (App. D.1, Alg. 1 line 12). It is Claude Opus 4.8 (§4.1).
- Code. A regex precheck runs first with a credential pattern and the patterns of the domain (`rrsi/critic.py:50` to `:52`, `:105` to `:119`). The coding patterns include every Terminal-Bench task name (`domains/coding/adapter.py:139` to `:141`).
- The LLM review rejects on six grounds. They are leakage, a degenerate or safety-removing change, grader gaming, undeclared bundling, runtime memory or skill leakage and unbounded work (`rrsi/critic.py:62` to `:95`).
- The review payload holds the candidate summary, the targeted modes, the declared edits and the diff (`rrsi/critic.py:123` to `:129`).
- A rejection returns the objections to the proposer for up to `repair_rounds` repairs. The value is five in every shipped `rrsi.json` (`rrsi/loop.py:500` to `:547`, `domains/coding/rrsi.json:18`, `domains/workspace/rrsi.json:9`, `domains/eng/rrsi.json:18`). A candidate still rejected is recorded without a measurement (`rrsi/loop.py:550` to `:552`).
- The regex precheck and the repair loop are not found in the paper.

### Step 5. Tag check and liveness check

- Code. A declared component tag is kept only when the diff carries a signal for it. Otherwise the tag is recomputed from the diff (`rrsi/components.py:82` to `:100`, `rrsi/loop.py:557` to `:558`). The candidate is then committed (`rrsi/loop.py:559` to `:560`).
- A liveness smoke check compiles the harness, constructs the agent and runs a few tasks before evaluation. A failure drops the candidate (`rrsi/loop.py:562` to `:568`).
- Coding runs two named tasks for one trial (`domains/coding/rrsi.json:28` to `:31`, `domains/coding/adapter.py:270`). Harvey LAB runs one production pass on the first two evolve tasks without the judge (`domains/workspace/split_workspace.py:137`, `domains/workspace/adapter.py:257` to `:268`). EngDesign runs four tasks for one trial (`domains/eng/rrsi.json:23`, `domains/eng/adapter.py:290`).
- The smoke check is not found in the paper.

## 3. How it decides to keep or reject a change

| check | rule | paper | code |
|---|---|---|---|
| change terms | `dS = S(H') - S(H_t)`, `dC = (C(H') - C(H_t)) / C(H_t)` | §3.3 Eq. 6 | `rrsi/selection.py:253` to `:254`, `rrsi/evaluate.py:131` to `:135` |
| noise-adjusted floor | `S(H') >= S* - delta`, with `S*` the best evolve score so far | §3.3 Eq. 5 | `rrsi/selection.py:258` to `:262` |
| gain above the band | if `dS > delta`, require `dC <= beta0 + beta1 * dS` | §3.3 Eq. 7 | `rrsi/selection.py:235` to `:240` |
| gain within the band | if `dS <= delta`, require `w_s * dS - w_c * dC + w_n * nu > 0` | App. D.3 Eq. 17 | `rrsi/selection.py:241` to `:245` |
| novelty `nu` | structural types among `client_tool`, `skill`, `memory`, `subagent` that the candidate touches and no accepted edit has touched | App. D.3 Eq. 15, Eq. 16 | `rrsi/components.py:103` to `:108`, `rrsi/history.py:129` to `:141` |
| domain guard | checks defined per domain | App. D.1 Alg. 2 line 13 | `rrsi/selection.py:267` to `:269` |
| selection | highest `S` among admissible candidates, otherwise keep `H_t` | App. D.3 | `rrsi/selection.py:284` to `:288`, `rrsi/loop.py:328` to `:340` |
| best score | `S* = max(S*, S(H_{t+1}))` | App. D.1 Alg. 2 line 19 | `rrsi/loop.py:335` |

- Only EngDesign defines guards in the code. A candidate fails when its valid rate falls by more than 0.03 or its no-submission rate rises by more than 0.02 (`domains/eng/adapter.py:221` to `:229`, `domains/eng/rrsi.json:24` to `:25`). The other domains return no guard (`rrsi/domain.py:78` to `:80`). The paper names no guard condition (App. D.1, App. D.3).
- The edits of the winning candidate are recorded with `a = 1` (App. D.2 Eq. 10). The code records the winner as `ACCEPTED`, an admissible loser as `LOST` and an inadmissible candidate as `REJECTED` (`rrsi/loop.py:318` to `:322`).
- The paper calls the cost rule Ridge or L2 style (§3.3) and calls it an L1 style budget in §4.3. The code comments call it the L1 cost rule (`rrsi/config.py:40`, `rrsi/calibrate.py:40`).

### Regularizer values

| symbol | Table 5 (coding, agentic workspace, engineering design) | `rrsi.json` (coding, workspace, eng) | code default |
|---|---|---|---|
| `T` | 20, 20, 40 | 20, 20, 40 (`coding:3`, `workspace:3`, `eng:3`) | 20 (`rrsi/config.py:59`) |
| `k` | 2, 2, 4 | 2, 2, 4 (`coding:4`, `workspace:3`, `eng:4`) | 2 (`rrsi/config.py:60`) |
| `m` | 2 (App. E.1) | 2, 2, 2 (`coding:5`, `workspace:3`, `eng:5`) | 2 (`rrsi/config.py:61`) |
| `delta` | 0.017, 0.004, 0.020 | 0.017, 0.004, 0.020 (`coding:10`, `workspace:5`, `eng:10`) | `None`, read from calibration (`rrsi/config.py:68`) |
| `b_min` | 1, 1, 1 | 1, 1, 1 (`coding:6`, `workspace:4`, `eng:6`) | 1 (`rrsi/config.py:63`) |
| `b_max` | 4, 3, 4 | 4, 3, 4 (`coding:7`, `workspace:4`, `eng:7`) | 4 (`rrsi/config.py:64`) |
| `w` | 3, 3, 3 | 3, 3, 3 (`coding:8`, `workspace:4`, `eng:8`) | 3 (`rrsi/config.py:65`) |
| `m_draft` | 1, 1, 1 | 1, 1, 1 (`coding:9`, `workspace:4`, `eng:9`) | 1 (`rrsi/config.py:66`) |
| `n_prune` | 4, 4, 5 | 4, 4, 5 (`coding:17`, `workspace:8`, `eng:17`) | 4 (`rrsi/config.py:75`) |
| `beta0` | 0.10, 0.10, 0.15 | 0.1, 0.10, 0.15 (`coding:12`, `workspace:6`, `eng:12`) | 0.10 (`rrsi/config.py:70`) |
| `beta1` | 44.5, 35.4, 24.4 | 44.5, 35.4, 24.4 (`coding:13`, `workspace:6`, `eng:13`) | 40.0 (`rrsi/config.py:71`) |
| `w_s` | not listed | 0.0, 1414.0, 244.0 (`coding:14`, `workspace:7`, `eng:14`) | 100.0 (`rrsi/config.py:72`) |
| `w_c` | not listed | 15.0, 15.0, 2.0 (`coding:15`, `workspace:7`, `eng:15`) | 15.0 (`rrsi/config.py:73`) |
| `w_n` | not listed | 0.5, 0.5, 0.5 (`coding:16`, `workspace:7`, `eng:16`) | 0.5 (`rrsi/config.py:74`) |

- In the table `coding:n`, `workspace:n` and `eng:n` are lines of `domains/<domain>/rrsi.json`.
- App. D.3 says the three weights `w_s`, `w_c` and `w_n` are reported in Table 5. Table 5 does not list them (App. E.1). App. D.3 says the coding instance sets `w_s` to zero and the other two use a positive `w_s`, which the `rrsi.json` values match.

### How the noise band is set

- Paper. The unchanged base harness is evaluated repeatedly before evolution to estimate `delta` (§3.3, App. D.1). For EngDesign `delta` is read off the first percentile of a null built by half-splitting the trials of the base evaluation (App. E.1).
- Code. `Run.delta` returns the fixed `delta` of `rrsi.json` and reads `calibration.json` only when `delta` is null (`rrsi/loop.py:102` to `:107`). The `baseline` command evaluates `H_0` once and calibrates on that one job (`rrsi.py:100` to `:102`).
- `rrsi/calibrate.py` sets `delta` to `z` times the standard deviation of the null score difference, with `z` from `delta_z` (`rrsi/calibrate.py:85` to `:104`, `rrsi/config.py:69`). With two or more base evaluations it uses their spread. With one it bootstraps over trials within tasks (`rrsi/calibrate.py:89` to `:104`).
- The separate script `domains/eng/bench/calibrate.py` takes the first percentile of a null that resamples each task from its own baseline pass rate (`domains/eng/bench/calibrate.py:118` to `:142`, `:259`). Its half-split null is a separate quantity (`domains/eng/bench/calibrate.py:87` to `:115`).

### How many runs, and on which tasks

- Paper. Each screened candidate is evaluated once on the full evolve set with `k` trials per task (App. D.1, Alg. 2 line 5). Coding uses `89 x k = 178` trials and EngDesign uses `61 x k = 244` trials. Harvey LAB uses roughly 14,100 criterion verdicts (App. E.1). Hyperparameters are set without consulting held-out or out-of-distribution benchmarks (App. E.1).
- Code. Each screened candidate is evaluated once on `evolve_ids()` with `cfg.k` trials (`rrsi/loop.py:244`, `:578` to `:605`). The incumbent is not run again. Its stored evaluation is the comparison point (`rrsi/loop.py:112` to `:113`, `:245`, `:306`). `H_0` is evaluated once by `baseline` (`rrsi/loop.py:181` to `:191`).
- An evaluation is repeated once when the share of missing trials exceeds `invalid_missing_frac`. If it still exceeds it, the candidate is dropped (`rrsi/loop.py:588` to `:602`). The values are 0.2, 0.1 and 0.15 (`domains/coding/rrsi.json:19`, `domains/workspace/rrsi.json:9`, `domains/eng/rrsi.json:19`).
- Paper. The candidates of a round are evaluated in parallel (App. D.1, Alg. 2 line 4). Code. `eval_parallel` is `1` in all three `rrsi.json` files, so the thread pool has one worker (`rrsi/loop.py:301` to `:302`, `domains/coding/rrsi.json:22`, `domains/workspace/rrsi.json:10`, `domains/eng/rrsi.json:22`).
- Paper. Eq. 3 divides both the score sum and the cost sum by `k|D_evolve|` (§2). Code. A missing trial counts as reward zero with the full denominator (`rrsi/evaluate.py:33` to `:36`, `:104` to `:119`). The cost is the mean over trials that carry a positive token count, so missing trials leave the cost denominator (`rrsi/evaluate.py:113`, `:117`). When either cost is absent, `dC` is zero (`rrsi/evaluate.py:131` to `:135`).
- Harvey LAB trials carry a weight equal to their criteria count, so `S` is the fraction of criteria passed (`rrsi/evaluate.py:38` to `:41`, `domains/workspace/adapter.py:203` to `:214`). App. B.3 defines the Harvey LAB score this way. Eq. 3 is written as an unweighted mean (§2).

## 4. What it executes

- The search runs the agent on the tasks. Each candidate runs on the evolve set with `k` trials per task and is scored by the benchmark's verifier (§2, App. D.1 Alg. 2 line 5, `rrsi/evaluate.py:122` to `:128`).
- Coding. The harbor CLI runs the candidate's Terminus-2 fork on Terminal-Bench 2.1 in Docker (`domains/coding/scripts/run_eval.sh:44` to `:53`, `domains/coding/adapter.py:154` to `:191`). The trial reward is the harbor verifier reward, 1.0 when the hidden tests pass (`domains/coding/adapter.py:34` to `:35`, `:74` to `:76`). App. B.1 describes the same test suite grading.
- Harvey LAB. Each of the `k` samples is one production pass of the archipelago react_toolbelt agent through an MCP gateway, followed by the Harvey LAB rubric judge (`domains/workspace/adapter.py:185` to `:190`, `domains/workspace/produce.sh:32`, `:40` to `:42`). `workspace_judge.py` calls the Harvey LAB `score_rubric` with a `Judge` of model `gemini-3.5-flash` and writes the passed and total criteria of each task (`domains/workspace/workspace_judge.py:49` to `:50`, `:61`, `:78` to `:88`). App. B.3 names the same judge model.
- EngDesign. `bench/run_tasks.py` runs the agent for `k` trials per task. `bench/verify.py` then runs the frozen verifier `frontier_eval/run_eval.sh` of each task (`domains/eng/adapter.py:154` to `:171`, `domains/eng/bench/verify.py:29` to `:34`, `:91` to `:96`). The reward is the verifier's `passed` flag (`domains/eng/adapter.py:202`). App. B.7 names grading by the task's own simulation or testbench with no judge model.
- The smoke check also runs the agent before evaluation (`rrsi/loop.py:562` to `:568`).
- The proposer runs no code. Its action set has no execution action (`rrsi/propose.py:71` to `:105`). The digester runs allowlisted read-only shell commands on rendered trace files (`rrsi/digester.py:51` to `:54`, `:203` to `:213`). The critic reviews the diff text and leaves runtime errors to the compile and smoke checks (`rrsi/critic.py:97` to `:100`).
- Outside the search loop, `heldout` evaluates a ref on the 40 Harvey LAB held-out tasks (`rrsi.py:115` to `:119`, `rrsi/loop.py:218` to `:228`). `swe_eval.sh` runs `H_0` and the incumbent on SWE-bench Verified with one attempt per instance (`domains/coding/scripts/swe_eval.sh:14` to `:33`). Its resolve rate is over the full 500 instances (`domains/coding/scripts/swe_eval.sh:15`).
- The JobBench, GDPval and APEX-Agents wrappers copy the harness into an external benchmark checkout and run that checkout's own driver and judge (`domains/workspace/ood/run_jobbench.sh:15` to `:34`, `domains/workspace/ood/run_gdpval.sh:15` to `:34`, `domains/workspace/ood/run_apex.sh:16` to `:32`).
- `final_eval.sh` runs `H_0` and the incumbent on EngDesign v1 and on Frontier-Eng (`domains/eng/scripts/final_eval.sh:15` to `:21`). An EngDesign v1 result is not found in the paper.

## 5. Models by step

| step | model in the paper | model in the code | source |
|---|---|---|---|
| analyst | Claude Opus 4.8 (§4.1) | `analyst_model`, default `claude-opus-4-8`, no temperature sent | `rrsi/config.py:83`, `rrsi/loop.py:263`, `rrsi/llm.py:107` to `:111` |
| digester | not found | the analyst model, no temperature sent | `rrsi/analyst.py:177` to `:179`, `rrsi/llm.py:107` to `:111` |
| proposer | Claude Opus 4.8 (§4.1) | `proposer_model`, default `claude-opus-4-8`, no temperature sent | `rrsi/config.py:82`, `rrsi/loop.py:493`, `:543`, `rrsi/llm.py:107` to `:111` |
| leakage critic | Claude Opus 4.8 (§4.1) | `critic_model`, default `claude-opus-4-8`, no temperature sent | `rrsi/config.py:84`, `rrsi/loop.py:505`, `rrsi/llm.py:107` to `:111` |
| policy, coding | Claude Opus 4.8 (§4.1), Gemini 3.5 Flash in a second run (§4.3, Table 3) | `policy_model` `vertex_ai/claude-opus-4-8`, fallback `vertex_ai/gemini-3.5-flash`, no temperature passed | `domains/coding/rrsi.json:23`, `domains/coding/adapter.py:181`, `domains/coding/scripts/run_eval.sh:44` to `:53`, `third_party/harbor_terminus2/terminus_2.py:211` to `:212` |
| policy, Harvey LAB | Claude Opus 4.8 (§4.1) | `ORCHESTRATOR_MODEL`, default `vertex_ai/claude-opus-4-8`, empty extra arguments | `domains/workspace/adapter.py:146` to `:147`, `domains/workspace/produce.sh:40`, `domains/workspace/workspace_driver.py:194` |
| policy, EngDesign | Claude Opus 4.8 (§4.1) | `ORCHESTRATOR_MODEL`, default `vertex_ai/claude-opus-4-8`, empty extra arguments with the comment "no temperature / reasoning_effort" | `domains/eng/config.py:64` to `:65` |
| policy for the transfer test | Gemini 3.1 Flash Lite (§4.3, Table 4) | not found | |
| Harvey LAB judge | Gemini-3.5-Flash (App. B.3) | `gemini-3.5-flash`, temperature not found in this repository | `domains/workspace/rrsi.json:14`, `domains/workspace/workspace_judge.py:56`, `:61` |
| JobBench judge | mean of Gemini-3.5-Flash and Claude Opus 4.8 (App. B.4) | not found, the benchmark's own judge in an external checkout | `domains/workspace/ood/run_jobbench.sh:21` |
| GDPval judges | Qwen3.6-35B-A3B, Claude Sonnet 4.6 and Gemini-3.1 Pro (App. B.5) | not found, the benchmark's own judge in an external checkout | `domains/workspace/ood/run_gdpval.sh:21` |
| APEX-Agents judge | Gemini-3.5-Flash (App. B.6) | not found, the benchmark's own rubric judge in an external checkout | `domains/workspace/ood/run_apex.sh:24` |
| Terminal-Bench 2.1 and SWE-bench Verified grading | unit tests, no model (App. B.1, App. B.2) | harbor verifier reward | `domains/coding/adapter.py:74` to `:76`, `domains/coding/scripts/swe_summary.py:46` to `:49` |
| EngDesign and Frontier-Eng grading | simulator or testbench, no judge model (App. B.7, App. B.8) | frozen per task verifier, no LLM | `domains/eng/bench/verify.py:29` to `:34`, `domains/eng/config.py:40` to `:44`, `domains/eng/scripts/final_eval.sh:20` |

- A temperature for any model is not found in the paper. The paper HTML contains no occurrence of "temperature".
- Search roles. `rrsi/llm.py` builds `anthropic.AnthropicVertex(project_id, region)` and calls `client.messages.create` (`rrsi/llm.py:59` to `:69`, `:107` to `:111`). The package is `anthropic[vertex]` (`pyproject.toml:24`).
- The projects come from `RRSI_VERTEX_PROJECTS` and the region from `RRSI_VERTEX_REGION`, with default `global` (`rrsi/llm.py:45` to `:49`). The code sets no base URL and no API key (`rrsi/llm.py:59` to `:69`). The README sets credentials with `gcloud auth application-default login` (`README.md:75`).
- A call is tried up to six times, rotating over the projects (`rrsi/llm.py:92`, `:103` to `:120`). `max_tokens` is 20,000 (`rrsi/llm.py:50`).
- `RRSI_SEARCH_MODEL` sets the model only for a call that passes none (`rrsi/llm.py:44`, `:95`). The loop always passes the role model from the config (`rrsi/loop.py:263`, `:493`, `:505`, `:543`).
- Coding policy. Harbor calls the model through its `LiteLLM` wrapper (`third_party/harbor_terminus2/terminus_2.py:48`, `:145`). `run_eval.sh` requires `VERTEXAI_PROJECT` and sets `VERTEXAI_LOCATION` with default `global` (`domains/coding/scripts/run_eval.sh:40` to `:41`).
- Harvey LAB and EngDesign policy. The archipelago runner calls `litellm.acompletion` (`third_party/archipelago/runner/utils/llm.py:21`, `:519`). It routes through a LiteLLM proxy only when `LITELLM_PROXY_API_BASE` and `LITELLM_PROXY_API_KEY` are set (`third_party/archipelago/runner/utils/llm.py:44` to `:46`).
- The Vertex project and location come from `VERTEX_PROJECT` and `VERTEX_LOCATION` (`domains/workspace/produce.sh:22` to `:25`, `domains/eng/config.py:57` to `:60`). EngDesign spreads trials over the projects in `ANTHROPIC_VERTEX_PROJECTS` (`domains/eng/config.py:71` to `:83`).
- Harvey LAB judge. The judge runs with `GOOGLE_GENAI_USE_VERTEXAI=true` and `GOOGLE_CLOUD_PROJECT` set from `VERTEX_PROJECT` (`domains/workspace/adapter.py:172` to `:175`). The `Judge` class is imported from the Harvey LAB checkout, not from this repository (`domains/workspace/workspace_judge.py:47` to `:49`).

## 6. Embedding model

- Not found in the paper. The paper HTML contains no occurrence of "embedding".
- Not found in the code. A case-insensitive search for "embedding" over the repository at be50316 returns no file.

## 7. How the paper scores the method

- Benchmarks. Eight benchmarks in three domains (§4, §4.1). Coding evolves on Terminal-Bench 2.1 and transfers to SWE-bench Verified. Agentic workspace evolves on Harvey LAB, is tested on its held-out split, and transfers to JobBench, GDPval and APEX-Agents. Engineering design evolves on EngDesign and transfers to Frontier-Eng.
- Terminal-Bench 2.1 reports the fraction of the 89 tasks whose own test suite passes (App. B.1). SWE-bench Verified reports the resolve rate over instances whose fail-to-pass and pass-to-pass tests both hold (App. B.2).
- Harvey LAB reports the fraction of rubric criteria passed over all tasks, each criterion judged by Gemini-3.5-Flash (App. B.3). JobBench reports the benchmark's weighted rubric score with the mean of two judges (App. B.4).
- GDPval reports the win rate against the human expert deliverable over 185 tasks, by majority vote of three judges in both presentation orders (App. B.5). APEX-Agents reports pass@1 over 480 tasks with a Gemini-3.5-Flash rubric judge (App. B.6).
- EngDesign is graded by each task's own simulation or testbench (App. B.7). App. E.1 counts it in passes. Frontier-Eng reports the Medal Score over the 47 tasks of its v1 set, of which 38 contribute credit (App. B.8).
- Figure 3 reports every number against `H_0` measured in the same window (§4.2).
- Table 1 compares RRSI with `H_0`, Meta-Harness, AHE, TTHE and HarnessX on the agentic workspace benchmarks (§4.2, App. C). Table 2 removes the proposal regularizers, the acceptance regularizers or both, and reports policy tokens per trial (§4.3).
- Table 3 repeats the coding evolution with Gemini 3.5 Flash as the policy. Table 4 runs that harness with Gemini 3.1 Flash Lite (§4.3). Figure 4 reports policy tokens and steps per trial (§4.3).
- Table 6 gives paired task-level bootstrap intervals over 10,000 resamples. Table 7 repeats every evolution run once (App. E.2). Table 8 and Table 9 show individual accept and reject decisions and final harness contents (App. F).
