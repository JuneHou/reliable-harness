# SelfHeal workflow

This note describes how the SelfHeal repair method (arXiv 2604.17699) and its repository run on the AgentDefect benchmark. A paper statement cites the paper section. A repository statement cites the file and line at commit 812e6a3 of `/data/wang/junh/githubs/SelfHeal`.

## 1. Building the dataset

- For each Stack Overflow or HuggingFace forum post, the SelfHeal authors added code so the bug reproduces (`run_buggy.py`). They wrote `run_fixed.py` from the accepted answer, a `test.py`, a readme with run steps and a `requirements.txt` with library versions (paper §4.2).
- The readme of case 77099194 says "Set your Openai Key there as `OPENAI_API_KEY`" and "Run the file `python3 run_buggy.py`" (`AgentDefect.zip`, `AgentDefect/77099194/readme.md`).
- `preproceesing/create_env.py` creates one virtualenv per case and installs that case's own `requirements.txt` (lines 35 and 42).
- An LLM wrote a one-line code intent per case from the post's title and body, and a human checked it (paper §4.2). The paper names GPT 5 Mini. The script calls `gpt-5-mini` (`preproceesing/create_intent.py:15`).

## 2. Building the fix rules

- Stage one writes one summary per training post from its title, body, rationale, fixed code and fixed requirement (`preproceesing/extract_summary.py:33` to `:49`). The script calls `gpt-5-mini` (`:64`). Posts of the test cases are skipped (`:57` to `:59`).
- Stage two joins the summaries of each fix pattern into one rule (`preproceesing/make_rules.py`). The script calls `o3-mini` (`:51`).
- The paper says "For rule generation, we used GPT 5 Mini" (§3.1). It does not mention o3-mini.

## 3. Repair loop

SelfHeal runs two LLM agents in turn, a fix agent that writes a new version of the code and a critic agent that accepts or rejects it (paper §3.2). Both are ReAct agents on the same model, and the code asks for temperature 0 (`run_agent.py:232` to `:278`). For a model name starting with `gpt-5`, langchain-openai v1.1.6 drops any temperature other than 1 (`langchain_openai/chat_models/base.py:841` to `:868`). So the GPT-5.2 path, which our runs use under the client name `gpt-5.2`, sends no temperature, and the Gemini path sends 0.

### 3.1 Fix agent

- It receives one prompt with the code intent and the full text of `run_buggy.py` (`run_agent.py:292`, `:306` to `:323`). The intent comes from `test_descriptions_with_intent.csv` (`:19`).
- The prompt says "IMPORTANT: This is NOT a crash bug. The issue is that the output does not match what the user expects." (`:310`).
- Its four tools list the fix pattern names, return the rule of one pattern from `fix_pattern_summaries.csv`, search the web and store the new code (`:247` to `:252`, `:18`, `:138`).
- It ends by calling the store tool with the complete new code. Nothing is run.

### 3.2 Critic agent

- It receives one prompt with the case number, the full text of `run_buggy.py` and the full text of `test.py` (`run_agent.py:334` to `:355`). The prompt tells it to call its three tools in order and then to "Respond with ACCEPT or REJECT and reasoning".
- When the text of `test.py` contains the word "Error", the code treats the test as missing and sends a prompt without it (`:334`, `:357` to `:374`). This holds for three AgentDefect cases, 78020395, 76379440 and 76456041.
- Tool one, `generate_diff`, returns the line differences between `run_buggy.py` and the stored new code (`:154` to `:174`).
- Tool two, `validate_fixed_code`, runs nothing and checks two strings (`:177` to `:198`). It returns REJECT when the new code holds no "def ", or holds no "return" while the test holds "assert". It returns REJECT when the test text holds "Error". Otherwise it returns "ACCEPT fixed code matches expected structure and output format".
- Tool three, `verify_api_usage`, takes a function name chosen by the critic and runs one web search for "<name> Python parameters return type documentation". It returns up to five result titles and snippets for the critic to read (`:201` to `:229`).
- The tools only return text. The critic's model writes the verdict. A round counts as accepted when the critic's last message holds the string "ACCEPT" anywhere (`:394`).

### 3.3 Rounds

- The loop runs at most three rounds (`run_agent.py:281`, `:300`). Each round builds a new fix agent and a new critic agent (`:303`).
- The paper says that after a rejection "the fix agent analyzes the reasoning and generates another version of the fixed code" (§3.2.2). In the code the next fix agent gets the same prompt as the first, and the critic's reasoning is not in it (`:306` to `:323`).
- When a round is accepted, the stored code is returned with the status ACCEPTED. After three rejected rounds, the last stored code is returned with the status FAILED (`:394` to `:419`).
- Models. GPT-5.2 through OpenAI, with the code's temperature 0 dropped as section 3 says (`run_agent.py:245`, `:270`). Gemini 3 Pro as `google/gemini-3-pro-preview` at temperature 0 through OpenRouter when `OPENROUTER_API_KEY` is set (`:237` to `:243`, `:262` to `:268`). Claude Sonnet 4 by editing the model name (`README.md`). The paper lists the three models in §4.1 and §4.3.1.

## 4. No program is run

- The paper says "SelfHeal does not execute code during debugging" (§4.4).
- `run_agent.py` opens `run_buggy.py` and `test.py` only as text (`:80` to `:111`). It contains no subprocess, exec or os.system call.
- `validate_fixed_code` checks that the fixed code contains "def " and, when the test contains "assert", "return" (`run_agent.py:188` to `:191`).
- No chat or embedding call inside an AgentDefect program is made in the repair loop.

## 5. Scoring

- The paper reports a resolution rate and localization at line, function and component level (§4.3.1). With Gemini 3 Pro, 22 of 37 cases are resolved.
- `Detailed Result.xlsx` holds a 0 or 1 per case for Line, Function, Component and Resolved, with Attempts and Time, one sheet per setting.
- The paper does not state how Resolved was decided. No script in the repository writes these columns. `run_agent.py` writes the status, the final code and the attempts of each case.

## 6. Embedding model in the AgentDefect programs

- The paper and the repository name no embedding model. The model is set only by the shipped program code and the package versions each case pins.
- Cases 78188862 and 79746620 name text-embedding-3-small in their code.
- The other 12 programs that embed with OpenAI call `OpenAIEmbeddings()` or `OpenAIEmbedding()` with no model. Every pinned version defaults to text-embedding-ada-002, for example `langchain/embeddings/openai.py:163` in langchain 0.0.245 and `langchain_openai/embeddings/base.py:169` in langchain-openai 1.1.6.

## 7. Difference from our earlier AgentDefect run

- Our earlier run used one shared environment (`motivation/configs/study.yaml`, `python: /data/wang/junh/envs/harnessfix/bin/python`) with langchain 0.3.30. Of the 14 programs that embed with OpenAI, 9 pin langchain 0.0.245.

## 8. Which file SelfHeal reads in AgentIssue-Bench

- In AgentDefect SelfHeal reads `run_buggy.py` and `test.py` from the case folder (`run_agent.py:86`, `:103`). An AgentIssue-Bench issue has no such file. Its buggy code is the agent system's repository at the buggy commit, inside the issue's Docker image.
- SelfHeal reads the repository files that the issue report names. Jun "let's give 1, document in method file", choosing this rule over the whole repository, a file picking step and running SelfHeal on AgentDefect only.
- No input comes from the developer fix. Jun "this is repair leakage", about giving SelfHeal the files the fix changes.
- The report is the issue's title and body in `motivation_experiment/artifacts/agentissue/issues/<tag>.json` of the AgentIssue-Bench folder. Comments are not used, because a comment can point to the fix. The only comment on agixt_1026 reads "This should be resolved now from PR #1027".
- A named file is a path or a file name with an extension in the report. It is matched to the repository at the buggy commit by comparing path parts from the file name backwards. The repository file with the longest matching run counts, and the run must hold at least the file name. A name that matches no repository file, such as a file of another package or of the reporter's own project, is left out. A name that ties between two repository files is left out.
- Of the 35 issues with a recorded developer fix in `devfix_stats.csv`, the report names a file that the fix changes in six. They are agixt_1026, agixt_1030, crewai_1270, haystack_8912, haystack_9523 and pythagora_55. This count compared file names only.
- When the report names several repository files, SelfHeal reads all of them. They are joined into one text, each file opened by a line that gives its repository path, and the code SelfHeal returns is split back into files at those lines.
- When the report names no repository file, the model picks the files from the issue's title and body and the list of repository files at the buggy commit. Jun "if not available, select 3". The picked files are read in the same way. The picking runs on the same model as the SelfHeal run, as the `Plan_bench.md` row on models sets for every role.
- The model picks files with the file-level prompt of Agentless, which the AgentIssue-Bench folder ships at commit 1d498dec (`Agentless/agentless/fl/FL.py:29` to `:48`). Jun "use this prompt". The prompt text is used unchanged. It asks for "a list of files that one would need to edit to fix the problem" and to "return at most 5 files".
- `{problem_statement}` is the issue's title and body. `{structure}` is the full path of every repository file at the buggy commit, one per line.
- The call uses temperature 0 and one sample, as Agentless does (`FL.py:335`, `:340`, `:343`). Each line of the reply that equals a repository path is a picked file, as in Agentless (`FL.py:346`, `:353`, `agentless/util/preprocess_data.py:684` to `:694`).
- The test text SelfHeal's critic reads is the reproduction script that the AgentIssue-Bench authors wrote for each issue (AgentIssue-Bench paper §4.1, "we manually write a test script"), stored inside the issue's image. It takes the place of `test.py`. For crewai_1532 its path is `/opt/reproduce.py` (`motivation_experiment/artifacts/agentissue/entrypoints.json`). Jun "yes".
- A repair is scored with the benchmark's own commands. Each returned file is diffed against the same file at the buggy commit to make a patch. The image's entrypoint applies it with `apply_patch` and runs the reproduction script on the patched code with `test_patched`. The repair passes when the output holds no "FAILED", the exit code is 0 and the output holds one of the benchmark's success messages, as in `eval_patches.py:117` and `:123` to `:128`, and `:79` and `:83` to `:89` for agixt_1369. Jun "yes".
- Agentless itself shows the model only Python files and leaves out test files (`agentless/fl/localize.py:49`, `:50`, `preprocess_data.py:389`, `:390`). That filter is not applied here, because Jun's choice gives the model the repository's file list.

## 9. Web search in our runs

- SelfHeal's search function (`run_agent.py:31` to `:69`) sends each query to DuckDuckGo through the `ddgs` package in place of SerpAPI. Jun "yes", choosing a free search with no new API key.
- Everything else in the function stays. It keeps up to five results, keeps each result's title and snippet, and drops results whose link holds stackoverflow.com. Both the fix agent's search tool (`:77`) and the critic's API check (`:220`) call it.
- The results come from DuckDuckGo. The paper used SerpAPI for Google Search (§4.1).

## 10. Inputs we rebuilt for AgentDefect

- The fix rules and the code intents need each post's title and body (`preproceesing/extract_summary.py:34` to `:49`, `preproceesing/create_intent.py:39`). Neither SelfHeal's repository nor the AgentDefect folder holds them. The other columns the fix rules use, `Rational`, `Fixed code` and `Fixed Requirement`, are in the StackOverflow sheet of `Fix Patterns.xlsx`.
- `AgentDefect/SelfHeal/inputs/fetch_posts.py` gets the id, title and body of each post from the public Stack Exchange API, the same three fields as the query in `preproceesing/get_ids.py:17` to `:21`. Jun "please continue with question1".
- `AgentDefect/SelfHeal/inputs/fix-pattern.csv` is the StackOverflow sheet of `Fix Patterns.xlsx` with the column `ID` renamed `id`, in 754 rows over 665 posts.
- `AgentDefect/SelfHeal/inputs/train_descriptions.csv` holds 660 of those 665 posts. The API returned no post for the other five (75873494, 76646276, 79028921, 79277755, 79371473). `extract_summary.py` merges on `id` with `how="left"`, so their summaries are written without a title and body (`:10` to `:14`).
- `AgentDefect/SelfHeal/inputs/test_descriptions.csv` holds all 37 cases. The 36 Stack Overflow cases come from the API. hf-26 comes from the HuggingFace forum topic 145964, its title and first post.
- `AgentDefect/SelfHeal/inputs/fetch_record.json` records the sources, the counts and the ids the API did not return.

## 11. What our SelfHeal run contains

- The SelfHeal paper has three parts. An empirical study of fix patterns (§2), the AgentDefect dataset (§4.2) and the SelfHeal method (§3). The method "consists of two main steps", fix rule generation (§3.1) and fixed code generation (§3.2).
- Our run executes the method steps only, once for each ARC model in turn. Jun "if no, why you ask me. rethink".
  - Fix rules. `extract_summary.py` and `make_rules.py` on `AgentDefect/SelfHeal/inputs/`, written to `AgentDefect/SelfHeal/<model>/rules/`.
  - Code intents. §3.2 takes "the code intent generated in Step 4.2", a dataset input that the release does not ship. `create_intent.py` rebuilds it, and the rebuild is recorded.
  - Repair loop. `run_agent.py` on all 37 cases, five reruns per case, each rerun in `AgentDefect/SelfHeal/<model>/<case>/rerun_<k>/`.
- No AgentDefect program is run, because "SelfHeal does not execute code during debugging" (§4.4). No check of each defect case is run for SelfHeal.
- Each rerun keeps SelfHeal's own record (status, final code, each round's verdict and code) and the relay log of every model request and reply.

## 12. How our run is built

- `AgentDefect/SelfHeal/code/driver.py` runs each step into the folder layout. `rules` builds the fix rules and the intents for one ARC model, and `repair` runs the loop for every case and rerun.
- SelfHeal's own code runs in `/data/wang/junh/envs/selfheal`, Python 3.10.19 with every pin of SelfHeal's `requirements.txt` installed as written. That file does not list `langgraph`, which `run_agent.py:12` imports. `langgraph` 1.1.6 is the version pip chose under those pins, and `ddgs` 9.16.1 serves the web search of section 9.
- `extract_summary.py` and `make_rules.py` run unchanged in `/data/wang/junh/envs/selfheal-openai028` with openai 0.28.1, because they call `openai.ChatCompletion.create`.
- `make_rules.py` writes `fix_pattern_rules.csv` (`:11`), and `run_agent.py` reads `fix_pattern_summaries.csv` (`:18`) with the same two columns. The driver copies the first to the second name.
- SelfHeal's readme runs `clean_data.py` once on the training file and once on the test file. `clean_data_test.py` is the second version, with the two file names switched.
- The only code change is the search function of section 9. `AgentDefect/SelfHeal/code/run_agent.py` holds it, and `run_agent.diff` shows it against commit 812e6a3.
- hf-26's rebuilt `run_buggy.py` is `AgentDefect/SelfHeal/inputs/hf-26_run_buggy.py`, with `hf-26_run_buggy.diff` against the shipped `run_fixed.py`. Besides the changes the `Plan_bench.md` row names, it adds `from langchain import hub`, which the forum post's `hub.pull` line needs.
- `AgentDefect/SelfHeal/code/relay.py` receives every model call, replaces the model name with the run's ARC model and forwards it to ARC as a streamed call with no length limit, because ARC caps replies that are not streamed. It joins the streamed reply into one ordinary reply for SelfHeal and saves the request with that reply. Each step and each rerun has its own relay log.
- `AgentDefect/SelfHeal/code/run_model.sh <model>` runs the rules step and then the repair step for one ARC model, detached from the session, with its progress in `AgentDefect/SelfHeal/run_<model>.log`. Every step resumes. Finished summaries, rules, intents and reruns are kept and not redone, so the same command continues a stopped run.
