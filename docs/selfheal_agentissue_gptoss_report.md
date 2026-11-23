# Repair Effects and Stochastic Variation in SelfHeal on AgentIssue-Bench

## 1. Goal

> **Research question.** How much evidence distinguishes repair effects from stochastic variation?

Repair methods call a language model at every step, so the same program can pass in one run and fail in the next. We cannot remove this stochastic variation, because we cannot change the model. A fix should therefore change only structural parts of the program, such as a code path, a tool or a library version, that have a strong causal or correlated effect on the outcome. We run nine published repair methods five times on every case of AgentDefect and AgentIssue-Bench with three models, to measure their baseline performance and collect data. From these runs we will build our own acceptance rule, which checks that a fix changes such a part and how many runs it takes to show that effect.

## 2. SelfHeal on AgentIssue-Bench

This report covers SelfHeal on AgentIssue-Bench and answers three questions.

- **Which passes are not real fixes.** Section 3 compares the critic's decision with the test, finds the issues where the test cannot tell a fix from no fix, and gives the reason each other run failed. It also looks at why SelfHeal fails when a fix needs changes in several files, a case its authors say needs changes to the method (SelfHeal paper §4.4).
- **Can an early signal save runs.** Sections 4 and 5 ask whether the critic's first answer can cut the cost of measuring the success rate without making the estimate wrong. They connect this idea to two papers.
- **What else changes the outcome.** Section 6 reports failed web searches, which decide which runs we repeat.

<!-- fold -->
### 2.1 How SelfHeal repairs a program

SelfHeal uses two AI agents that run on the same language model. The fix agent writes a fix, and the critic agent reviews it (SelfHeal paper §3.2).

- **Before any repair.** The authors collected forum posts about past bugs and their fixes. A language model turns these posts into short fix rules, one rule for each kind of fix (§3.1).
- **Writing the fix.** The fix agent reads the buggy code and one sentence that says what the code should do. It may look up the fix rules and search the web. It then writes a full new version of the code.
- **Reviewing the fix.** The critic agent reads the buggy code and the test file. It looks at what the fix changed, runs a simple format check and may search the web to see how a function is used. It then answers ACCEPT or REJECT.
- **When the critic accepts.** The prompt only asks the critic to answer ACCEPT or REJECT with its reasons, so its language model decides from what its three tools return. SelfHeal counts an attempt as accepted when the answer contains the word ACCEPT in capitals.
- **The format check.** This check does not run the code. It only checks that the new code defines a function and, when the test contains an assert statement, returns a value.
- **If the critic accepts.** The run stops, and the new code is SelfHeal's repair. SelfHeal marks the run ACCEPTED.
- **If the critic rejects.** A new fix agent starts again from the same instructions and does not see why the critic rejected the fix. SelfHeal allows three tries. After the third rejection, it keeps the last fix and marks the run FAILED.
- **No running.** SelfHeal never runs the program while it repairs it (§4.4).
- **How the paper scores it.** The paper reports how many cases were resolved but does not say how it decided that a case was resolved (§4.3.1).
- **How we score it.** We run the benchmark's test once on every repair. A run counts as a success when the critic accepted the fix and the test passes.
- **What we changed in the code.** On AgentIssue-Bench, the web search uses DuckDuckGo in place of SerpAPI. We also changed the fix instructions and the format check so that SelfHeal can read and return several files (Table 1). A small relay program on our machine sends every model request to ARC and saves each answer.

### 2.2 Setup of SelfHeal on AgentIssue-Bench

**Table 1.** SelfHeal on AgentIssue-Bench in our runs compared with the published SelfHeal (arXiv 2604.17699) and AgentIssue-Bench (arXiv 2505.20749).

| component | as published | our runs | compared with the original |
|---|---|---|---|
| models | GPT-5.2, Gemini 3 Pro, Claude Sonnet 4. Rules by GPT 5 Mini | gpt-oss-120b, DeepSeek-V4.1-Flash, GLM-5.3. Part of the DeepSeek-V4.1-Flash runs on OpenRouter | changed |
| code SelfHeal reads | one buggy program | files the issue names (20 issues) or the model picks (30 issues), one header line per file | changed |
| code intent | written by GPT 5 Mini, checked by a human | written by the run's model from the issue, no human check | changed |
| test the critic reads | the authors' test file | the benchmark's reproduction script | changed |
| fix prompt and format check | Python only, checks for `def ` and `return` | any language, one header per file, structural check | changed |
| output | one complete program | split back into files at the headers | changed |
| web search | SerpAPI | DuckDuckGo | changed |
| runs | one per case | five per issue and model, a failed search repeated once | changed |
| scoring | resolution rate, no stated rule | critic accepts and the shipped test passes. The rate is q | changed |
| executing the original code | none | five runs of the buggy code through an empty patch, with no repair | changed |
| model calls inside the test | an OpenAI key | relay to ARC | changed |
| fix rules | the authors' rule sheet | the authors' rule sheet, rules written by the run's model | changed |
| repair loop | fix agent and critic, at most three attempts | as published | same |
| critic | the code omits the critic's reasons from the next fix prompt, although the paper says the fix agent uses them | as the code | same |
| program execution during repair | none | none | same |
| search results | top five, stackoverflow.com dropped | as published | same |
| test command and pass rule | `apply_patch` then `test_patched`, 300 seconds | as published | same |
| evaluator | the shipped scripts | the shipped scripts | same |

Notes. The Stack Exchange API returned no text for five posts of the authors' rule sheet, 75873494, 76646276, 79028921, 79277755 and 79371473, so their title and body were skipped.

## 3. Results of SelfHeal on AgentIssue-Bench with gpt-oss-120b

Each issue has two sets of test runs, both with the benchmark's test.

- **Executing the original code.** Five runs of the original buggy code through an empty patch, with no repair.
- **Executing the repair.** SelfHeal runs five times and gives five repairs, and each repair is executed once, 250 in all.

Executing the original code shows whether the test already passes without any fix.

### 3.1 Success is rare

With gpt-oss-120b, SelfHeal succeeded in 9 of 250 repair runs (Table 2). In 45 of the 50 issues no run succeeded. Table 2 compares SelfHeal's own decision, the critic's verdict, with the test result.

**Table 2.** Final SelfHeal verdict and shipped test result for the 250 repair runs with gpt-oss-120b.

| accepted, test passes | accepted, test fails | rejected, test passes | rejected, test fails | no result |
|---|---|---|---|---|
| 9 | 58 | 38 | 144 | 1 |

- **accepted, rejected.** The critic's decision. The critic reads the code, the change and the test file without running the program. It accepts at one of three attempts, or rejects all three, and SelfHeal then returns the third attempt's code.
- **test passes, test fails.** The benchmark's reproduction script runs on the repository with the returned code and passes when it reports no failure and shows a success message within 300 seconds. Some tests call the language model, so the same code can pass in one run and fail in the next. Every returned code is tested, accepted or not.
- **no result.** SelfHeal wrote no result file, so the run has no repair to test.

The shipped test passed in 47 runs, and SelfHeal accepted 9 of them. SelfHeal also accepted 58 repairs that failed the test.

### 3.2 Some tests pass without any fix

Table 3 splits the repair runs of Table 2 by what executing the original code showed for their issue.

**Table 3.** The 250 repair runs with gpt-oss-120b, five per issue, by the result of executing the original code of their issue.

| group | runs | accepted, test passes | accepted, test fails | rejected, test passes | rejected, test fails | no result |
|---|---|---|---|---|---|---|
| fails without a fix | 200 | 1 | 57 | 5 | 137 | 0 |
| passes without a fix | 50 | 8 | 1 | 33 | 7 | 1 |
| unstable | 0 | 0 | 0 | 0 | 0 | 0 |

- **fails without a fix.** The test failed on the original code in all five runs, so a pass of a repair can come from the repair.
- **passes without a fix.** The test passed on the original code in all five runs, so a pass of a repair shows nothing.
- **unstable.** The test passed on the original code in some of the five runs and failed in others.

Eight of the nine successes came from the ten issues whose test passes without a fix. In the 40 issues whose test fails without a fix, SelfHeal succeeded once in their 200 runs.

### 3.3 Why repairs fail the test

This subsection asks why SelfHeal's repairs fail the test. Table 4 gives each repair run one reason for its result, the first that applies in the table's order. A run without a repair comes first. Runs of issues whose test passes without a fix or is unstable come next, because their result says nothing about the repair. Every other run either passed or gets the reason it failed.

**Table 4.** Cause of each outcome for the 250 runs with gpt-oss-120b, by final SelfHeal verdict.

| cause | runs | accepted | rejected | no result |
|---|---|---|---|---|
| no repair | 1 | 0 | 0 | 1 |
| test passes without a fix | 49 | 9 | 40 | 0 |
| test unstable | 0 | 0 | 0 | 0 |
| test passed | 6 | 1 | 5 | 0 |
| did not receive every file the fix touches | 80 | 23 | 57 | 0 |
| omitted a file it received | 66 | 2 | 64 | 0 |
| patch did not apply | 6 | 2 | 4 | 0 |
| changed fewer source files than the fix | 1 | 0 | 1 | 0 |
| same last failure line as the buggy code | 37 | 27 | 10 | 0 |
| other failure | 4 | 3 | 1 | 0 |

- **no repair.** The run had no input file, no SelfHeal result or no tested repair.
- **test passes without a fix, test unstable.** The group of the issue, as defined for Table 3.
- **test passed.** The repair passed a test that fails without a fix.
- **did not receive every file the fix touches.** SelfHeal's input lacked a source file that the developer's fix changes. This cause applies to fixes of one to seven source files.
- **omitted a file it received.** The final code lacked the header line of a file SelfHeal received, so that file stayed unchanged.
- **patch did not apply.** The test log reports a rejected patch, a failed hunk, a missing file or no patch program.
- **changed fewer source files than the fix.** The repair changed fewer source files than the developer's fix touches, for fixes of one to seven source files.
- **same last failure line as the buggy code.** The last error line of the test log equals that of a run of the original code of the same issue and model, after digits, paths and hexadecimal ids are removed.
- **other failure.** Any failure the causes above do not cover.
- **source file.** A Python, TypeScript, JavaScript, Go, C#, Java, Rust or shell file outside test and documentation folders.

The test passed in 6 of the 200 runs on the 40 issues whose test fails without a fix. Of the 194 failures, 80 came from runs missing a file the fix touches and 66 from runs whose final code omitted a received file. The patch did not apply in six runs, and one repair changed fewer source files than the fix. Of the rest, 37 ended with the same last failure line as the original code and 4 failed otherwise. SelfHeal accepted 27 of those 37.

**Table 5.** Runs with gpt-oss-120b on the 40 issues whose test fails without a fix, five per issue, by the number of source files the developer's fix touches.

| files the fix touches | runs | SelfHeal received every fix file | test passed |
|---|---|---|---|
| one file | 50 | 25 | 5 |
| two to seven files | 65 | 10 | 0 |
| more than seven files | 70 | n/a | 1 |
| no source file | 15 | n/a | 0 |

- **files the fix touches.** Source files that the developer's fix changes. For a fix of more than seven source files, the set of files the repair needs is treated as unknown.
- **no source file.** The developer's fix changes only test, documentation or other files that are not source files.
- **SelfHeal received every fix file.** Runs whose input held every source file the fix touches. The count is n/a when that set is unknown or empty.
- **test passed.** Runs whose repair passed the shipped test.

SelfHeal received every file the fix touches in 25 of the 50 runs whose fix touches one file and in 10 of the 65 runs whose fix touches two to seven files. Five runs passed where the fix touches one file, and one where it touches more than seven. Across all 50 issues, 204 runs with a result received two or more files. In 160 of them the final code omitted a received file, and SelfHeal accepted 4 of those 160.

### 3.4 What each fix changed

A fix can only work when it changes the structural part that causes the failure. This subsection compares the source files each repair changed with the source files the developer's fix changes.

**Table 6.** Runs with gpt-oss-120b on the 40 issues whose test fails without a fix, by whether the repair changed the source files the developer's fix changes.

| repair changed | runs | test passed | successes |
|---|---|---|---|
| every file the fix changes | 22 | 5 | 1 |
| some of those files | 39 | 0 | 0 |
| none of those files | 54 | 0 | 0 |
| fix changes more than seven files | 70 | 1 | 0 |
| fix changes no source file | 15 | 0 | 0 |

- **every file the fix changes.** The repair changed every source file that the developer's fix changes, and possibly other files.
- **some of those files, none of those files.** The repair changed only part of those files, or none of them.
- **fix changes more than seven files, fix changes no source file.** The developer's fix gives no usable set of files, as in Table 5.
- **test passed, successes.** As defined for Table 2.

Runs that changed every file the developer's fix changes passed the test in 5 of 22 runs. Runs that changed only some or none of those files never passed. SelfHeal's critic accepted one of the five passing repairs.

## 4. Early signal from SelfHeal's critic on AgentIssue-Bench with gpt-oss-120b

SelfHeal's critic reviews the code of each attempt and either accepts it or asks for another attempt, up to three attempts in all. This section asks whether an early signal can lower the cost of estimating q to a given precision.

The definition of q already provides one saving. A rejected run counts as a failure, so only accepted runs need a test. On the 40 issues whose test fails without a fix SelfHeal accepted 58 runs and rejected 142. Testing only the 58 accepted runs yields the same q, 1 of 200, and saves 142 tests. An early signal has to improve on this saving.

**Table 7.** SelfHeal time and shipped test time for the runs with gpt-oss-120b that recorded both.

| issues | runs | SelfHeal minutes per run | test minutes per run | test share of total time |
|---|---|---|---|---|
| 40 that fail without a fix | 191 | 8.43 | 0.73 | 0.079 |
| all 50 | 238 | 8.70 | 0.70 | 0.075 |

- **runs.** Runs with both a SelfHeal time and a shipped test time on record.
- **SelfHeal minutes per run.** The time of all attempts of a run, averaged over these runs.
- **test minutes per run.** The time of the shipped test, averaged over these runs.
- **test share of total time.** Test time divided by the sum of SelfHeal time and test time over these runs.

Skipping every test would reduce the total time by less than a tenth, because most of the cost lies in the SelfHeal run itself.

**Table 8.** Runs with gpt-oss-120b and a result file, by the critic's verdict on attempt 1.

| issues | runs | accepted at attempt 1 | successes | rejected at attempt 1 | successes | attempt 1 share of SelfHeal time |
|---|---|---|---|---|---|---|
| 40 that fail without a fix | 200 | 36 | 1 | 164 | 0 | 0.37 |
| all with a result | 249 | 43 | 7 | 206 | 2 | 0.37 |

- **accepted at attempt 1.** The critic accepted the first attempt, which ends the run.
- **rejected at attempt 1.** The critic rejected the first attempt, and the run went on to attempt 2.
- **successes.** Runs in the column to the left that the critic accepted at some attempt and that passed the shipped test.
- **attempt 1 share of SelfHeal time.** The time of attempt 1 summed over runs, divided by the time of all attempts summed over runs.

The verdict on attempt 1 arrives after 0.37 of SelfHeal's time, both on the 40 issues whose test fails without a fix and on all issues. After a rejection, attempts 2 and 3 take the remaining 0.63 of the time. This is the time an early signal could save. Rejected runs still hold 2 of the 9 successes, both accepted at attempt 2. Stopping every rejected run would therefore bias q, while continuing a random share of them keeps it unbiased.

Stopping SelfHeal after attempt 1 yields 7 successes in 249 runs, and stopping after attempt 2 yields 9, the same as the full loop. Attempt 3 added no success.

## 5. SelfHeal's early signal and two papers

### 5.1 Where an early signal helps

The design question is where to spend the expensive part of each run. Suppose the runs that receive the full outcome are chosen at random with a probability fixed in advance. A signal that disagrees with the test then costs precision and leaves the estimate unbiased.

### 5.2 Within-run randomization

Sawarni et al. (arXiv 2611.09792) randomize an intervention with a known probability at each eligible decision within a run. They let the run continue and estimate the value of a policy from those runs (§2.2 eq. 2, §2.3 eq. 5). Their ImpossibleBench study is the closest to SelfHeal. After each of the first five failed code submissions, it assigns a neutral note or adversarial feedback at random (§3.3). Their Appendix A.2 states that "When the propensity e(h) is known, the score stays conditionally unbiased even when the outcome predictions are wrong."

- **Cost.** In SelfHeal the eligible decision is a rejection at attempt 1. The run continues with a probability fixed in advance and stops otherwise, and each continued run is weighted by the inverse of that probability. This estimates the q of SelfHeal as published and skips attempts 2 and 3 in the stopped runs. Other signals from attempt 1, such as the critic's text, the files changed or a module check, enter only through the outcome model. They narrow the interval and leave the target unchanged.
- **Repair effect.** Here the intervention is the retry with the critic's feedback, and their policy gain asks whether it helps. Because stopping ends a run, the q of stopping after each attempt is already known for every recorded run without randomization (Section 4). Randomization becomes necessary when both arms continue, for example the critic's feedback against a neutral note, which mirrors their neutral and adversarial feedback.

### 5.3 Surrogate outcomes

Athey et al. (arXiv 1603.09326) conclude that surrogates "can also greatly improve the precision of estimates even in settings where the treatment effect on the long-term outcome can be estimated directly, particularly when that outcome is rare or noisy." Success with gpt-oss-120b is rare, at 9 of 250 runs.

- **Source of the gain.** By their Remark 7, the gain equals the outcome noise left after the surrogate index, the term with (Y − μ(S,X))², which the index removes.
- **Assumption.** When signal and outcome are observed in the same runs, their Theorem 3(ii) gives the gain from assuming surrogacy. Their Remark 9 says this gain "captures just the value of the surrogacy assumption." Surrogacy means that a configuration changes success only through the signal.
- **Fit to this study.** Surrogacy concerns a treatment, so the gain applies to a difference in q between two configurations, which is the comparison the research question requires. For the q of a single configuration, continuing a random share of rejected runs needs no such assumption.
- **Testing the assumption.** Their Remark 1 makes surrogacy testable once two configurations have full outcomes, and DeepSeek-V4.1-Flash will provide the second. Their Section 3.2.3 favours several surrogates over one, so the test would combine the verdict with the critic's text and the files changed. With nine successes, the test has little power to detect a violation.

### 5.4 Proposed check

The following steps are proposed and have not yet been run.

- The signal is the attempt 1 verdict, and the probability of continuing after a rejection is fixed before any run. No predictor is learned.
- A resampling check on the 249 recorded runs needs no new model calls. It repeatedly draws stop or continue for each rejected run and compares the interval of the weighted q with plain subsamples of equal SelfHeal time.
- New runs with gpt-oss-120b would then follow the frozen design, and a second configuration would enter when the target is a difference in q.
- With nine successes, a small continuation probability widens the interval. The saving may therefore remain well below the 0.63 of the time that attempts 2 and 3 take on the 40 issues whose test fails without a fix.

## 6. Web search of SelfHeal on AgentIssue-Bench with three models

SelfHeal's fix agent searches the web through a search tool, and its critic searches the web when it verifies API usage. SelfHeal's published code places no limit on the number of searches. The fix agent is a LangGraph ReAct agent run with default settings, so its only ceiling is LangGraph's default limit of 10007 steps in our environment.

**Table 9.** Web searches by the fix agent and the critic in the AgentIssue-Bench runs of three models.

| model | searches | share that failed | median per run | most in one run | runs with a failed search | expected if each search fails independently |
|---|---|---|---|---|---|---|
| gpt-oss-120b | 1438 | 0.017 | 4 | 68 | 0.11 | 0.13 |
| DeepSeek-V4.1-Flash | 25533 | 0.026 | 52.5 | 1030 | 0.66 | 0.67 |
| GLM-5.3 | 2288 | 0.027 | 21 | 113 | 0.45 | 0.47 |

- **searches.** Replies of the fix agent's search tool and of the critic's API check in the run logs, from kept runs and from runs set aside for repetition.
- **share that failed.** The share of searches whose reply reports a search error.
- **median per run, most in one run.** Taken over runs with at least one search.
- **runs with a failed search.** The share of runs with at least one search in which at least one search failed.
- **expected if each search fails independently.** The mean over runs of 1 − (1 − p)ⁿ, where p is the model's share of failed searches and n is the run's number of searches.
- **DeepSeek-V4.1-Flash and GLM-5.3.** Their counts were taken while their runs were still in progress.

Of the 759 failed searches, 756 were timeouts on html.duckduckgo.com. Searches failed at a similar rate for all three models. DeepSeek-V4.1-Flash searched far more often per run, so most of its runs met at least one timeout, a share that matches the prediction for independent failures. A run with a failed search is repeated once, and a second failure is kept as it is.

## 7. Data and code

Every number in this report is computed from the run records under `AgentIssue-Bench/SelfHeal/` by `docs/selfheal_agentissue_gptoss_report_numbers.py`, and its registry gives the source of each number. The success rule is in `score_tests.py` line 107, the runs of the original code in `calibrate.py` and `calibrate_original.py` and the cause assignment in `analyze_multifile.py`. SelfHeal's search tools are in its `run_agent.py` lines 204 to 229, the fix agent in lines 247 to 254 and 325 to 328, and the attempt limit in line 281. LangGraph's step limit is in `_config.py` line 31. The full list of differences from the original repositories and papers, with the evidence for each, is in `docs/selfheal_deployment.md` section 5, and the project plan is `Plan_bench.md`.
