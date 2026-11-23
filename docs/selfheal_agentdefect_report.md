# Repair Effects and Stochastic Variation in SelfHeal on AgentDefect

## 1. Goal

> **Research question.** How much evidence distinguishes repair effects from stochastic variation?

Repair methods call a language model at every step, so the same program can pass in one run and fail in the next. We cannot remove this stochastic variation, because we cannot change the model. A fix should therefore change only structural parts of the program, such as a code path, a tool or a library version, that have a strong causal or correlated effect on the outcome. We run nine published repair methods five times on every case of AgentDefect and AgentIssue-Bench with three models, to measure their baseline performance and collect data. From these runs we will build our own acceptance rule, which checks that a fix changes such a part and how many runs it takes to show that effect.

## 2. SelfHeal on AgentDefect

This report covers SelfHeal on AgentDefect and answers three questions.

- **Which passes are not real fixes.** Section 3 compares the critic's decision with the test, finds the cases where the test cannot tell a fix from no fix, and gives the reason each other run failed.
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
- **How we score it.** We run the case's test once on every repair. A run counts as a success when the critic accepted the fix and the test passes.
- **What we changed in the code.** On AgentDefect, we changed only the web search, which uses DuckDuckGo in place of SerpAPI (Table 1). A small relay program on our machine sends every model request to ARC and saves each answer.

### 2.2 Setup of SelfHeal on AgentDefect

**Table 1.** SelfHeal on AgentDefect in our runs compared with the published SelfHeal (arXiv 2604.17699).

| component | as published | our runs | compared with the original |
|---|---|---|---|
| models | GPT-5.2, Gemini 3 Pro, Claude Sonnet 4. Rules by GPT 5 Mini | gpt-oss-120b, DeepSeek-V4.1-Flash, GLM-5.3 | changed |
| fix rules | the authors' rule sheet | the authors' rule sheet, rules written by the run's model | changed |
| code intent | written by GPT 5 Mini, checked by a human | written by the run's model, no human check | changed |
| hf-26 buggy program | missing | rebuilt from the forum post | changed |
| web search | SerpAPI | DuckDuckGo | changed |
| runs | one per case | five per case and model, a failed search repeated once | changed |
| scoring | resolution rate, no stated rule | critic accepts and the test exits with 0. The rate is q | changed |
| executing the original program | none | five runs of the buggy program, with no repair | changed |
| test environments | one per case | one per shared requirement list, 15 lists. Missing dependencies added, two lists adjusted so the programs load | changed |
| test fixtures | named in the readmes | Ollama for two cases, pgvector for one, tesseract for one, a missing PDF for one. Two tests import the repair | changed |
| model calls inside the test | the authors' OpenAI key | chat calls to ARC through a relay, embedding calls to OpenAI | changed |
| cases scored | 37 | 36. 79776520 needs keys we lack, hf-26 lacks a HuggingFace token | changed |
| completions endpoint | served by OpenAI | rejected by ARC, affects three cases | changed |
| dataset | AgentDefect, 37 cases | as published | same |
| code SelfHeal reads | the buggy program | as published | same |
| test the critic reads | the case's test file | as published | same |
| fix prompt and format check | from the code | as published | same |
| output | one complete program | as published | same |
| repair loop | fix agent and critic, at most three attempts | as published | same |
| critic | the code omits the critic's reasons from the next fix prompt, although the paper says the fix agent uses them | as the code | same |
| program execution during repair | none | none | same |
| search results | top five, stackoverflow.com dropped | as published | same |

Notes. The Stack Exchange API returned no text for five posts of the authors' rule sheet, 75873494, 76646276, 79028921, 79277755 and 79371473, so their title and body were skipped.

## 3. Results of SelfHeal on AgentDefect with gpt-oss-120b

Each case has two sets of test runs, both with the case's test.

- **Executing the original program.** Five runs of the original buggy program, with no repair.
- **Executing the repair.** SelfHeal runs five times and gives five repairs, and each repair is executed once, 180 in all.

Executing the original program shows whether the test already passes without any fix.

### 3.1 SelfHeal succeeds in under a third of runs

With gpt-oss-120b, SelfHeal succeeded in 54 of 180 repair runs (Table 2). In 18 of the 36 cases no run succeeded. Table 2 compares SelfHeal's own decision, the critic's verdict, with the test result.

**Table 2.** Final SelfHeal verdict and test result for the 180 repair runs with gpt-oss-120b.

| accepted, test passes | accepted, test fails | rejected, test passes | rejected, test fails | no result |
|---|---|---|---|---|
| 54 | 84 | 0 | 42 | 0 |

- **accepted, rejected.** The critic's decision. The critic reads the code, the change and the test file without running the program. It accepts at one of three attempts, or rejects all three, and SelfHeal then returns the third attempt's code.
- **test passes, test fails.** The test file the dataset authors wrote for the case calls the returned program, which itself calls the language model, and checks its output. The same code can pass in one run and fail in the next. Every returned program is tested, accepted or not.
- **no result.** SelfHeal wrote no result file, so the run has no repair to test.

The test passed in 54 runs, and SelfHeal accepted all 54. SelfHeal also accepted 84 repairs that failed the test.

### 3.2 Some tests pass without any fix

Table 3 splits the repair runs of Table 2 by what executing the original program showed for their case.

**Table 3.** The 180 repair runs with gpt-oss-120b, five per case, by the result of executing the original program of their case.

| group | runs | accepted, test passes | accepted, test fails | rejected, test passes | rejected, test fails | no result |
|---|---|---|---|---|---|---|
| fails without a fix | 135 | 24 | 70 | 0 | 41 | 0 |
| passes without a fix | 40 | 28 | 11 | 0 | 1 | 0 |
| unstable | 5 | 2 | 3 | 0 | 0 | 0 |

- **fails without a fix.** The test failed on the original program in all five runs, so a pass of a repair can come from the repair.
- **passes without a fix.** The test passed on the original program in all five runs, so a pass of a repair shows nothing.
- **unstable.** The test passed on the original program in some of the five runs and failed in others.

Of the 54 successes, 28 came from the eight cases whose test passes without a fix, and two came from the one unstable case. In the 27 cases whose test fails without a fix, SelfHeal succeeded in 24 of 135 runs.

**The case, AgentDefect 77099194**
- **Program.** A movie question-answering agent. It loads `movies.csv`, retrieves rows that match the question, and asks the language model to answer from them.
- **Bug.** It retrieves only one row, `search_kwargs={"k": 1}`. Asked for all action movies, it names just one.
- **Authors' fix.** A one-line change to `{"k": 12}`, so it retrieves 12 rows.
- **Test, written by the dataset authors.** It asks "Return all the action movies names". It passes only if the answer contains both "avengers" and "the dark knight rises".

**Executing the original program, five runs, none passed**

Every run failed. Each answer was only `avengers: age of ultron`, and the test reported `'the dark knight rises' not found`. So the test catches the bug.

**Executing the repair, SelfHeal's five repairs, each executed once, three passed**

SelfHeal rewrote about 40 lines each time. The critic accepted all five, but the test results differ.

**Table 4.** SelfHeal's five repairs of case 77099194 with gpt-oss-120b, each executed once.

| repair | rows retrieved (k) | test | test output |
|---|---|---|---|
| 1 | 5 | failed | "the dark knight rises" not found, the answer lists five movies without it |
| 2 | 5 | failed | same as repair 1 |
| 3 | 10 | passed | OK |
| 4 | 10 | passed | OK |
| 5 | 10 | passed | OK |

**What the two sets show together**
- The test failed on the original program every time, so the three passes come from the repairs.
- The difference between passing and failing repairs is one structural setting, how many rows are retrieved. Repairs that set 10 rows passed, and repairs that set 5 rows failed.
- The critic accepted all five, so it could not tell them apart.

### 3.3 Why repairs fail the test

This subsection asks why SelfHeal's repairs fail the test. Table 5 gives each repair run one reason for its result, the first that applies in the table's order. A run without a repair comes first. Runs of cases whose test passes without a fix or is unstable come next, because their result says nothing about the repair. Every other run either passed or gets the reason it failed.

**Table 5.** Cause of each outcome for the 180 runs with gpt-oss-120b, by final SelfHeal verdict.

| cause | runs | accepted | rejected | no result |
|---|---|---|---|---|
| no repair | 0 | 0 | 0 | 0 |
| test passes without a fix | 40 | 39 | 1 | 0 |
| test unstable | 5 | 5 | 0 | 0 |
| test passed | 24 | 24 | 0 | 0 |
| did not receive every file the fix touches | 0 | 0 | 0 | 0 |
| omitted a file it received | 0 | 0 | 0 | 0 |
| patch did not apply | 0 | 0 | 0 | 0 |
| changed fewer source files than the fix | 0 | 0 | 0 | 0 |
| same last failure line as the buggy program | 63 | 52 | 11 | 0 |
| other failure | 48 | 18 | 30 | 0 |

- **no repair.** The run had no SelfHeal result or no tested repair.
- **test passes without a fix, test unstable.** The group of the case, as defined for Table 3.
- **test passed.** The repair passed a test that fails without a fix.
- **did not receive every file the fix touches.** SelfHeal's input lacked a source file that the fixed program changes.
- **omitted a file it received.** The final code lacked a file SelfHeal received.
- **patch did not apply.** The test log reports a rejected patch, a failed hunk, a missing file or no patch program.
- **changed fewer source files than the fix.** The repair left the program unchanged where the fixed program changes it.
- **same last failure line as the buggy program.** The last error line of the test log equals that of a run of the original program of the same case and model, after digits, paths and hexadecimal ids are removed.
- **other failure.** Any failure the causes above do not cover.
- **source file.** A Python, TypeScript, JavaScript, Go, C#, Java, Rust or shell file outside test and documentation folders.

The test passed in 24 of the 135 runs on the 27 cases whose test fails without a fix. Of the 111 failures, 63 ended with the same last failure line as the original program, and SelfHeal accepted 52 of them. The other 48 failed otherwise, and SelfHeal accepted 18 of them. No failing run missed a file, omitted a file or left the program unchanged.

**Table 6.** Runs with gpt-oss-120b on the 27 cases whose test fails without a fix, five per case, by the number of source files the fixed program changes.

| files the fix touches | runs | SelfHeal received every fix file | test passed |
|---|---|---|---|
| one file | 135 | 135 | 24 |
| two to seven files | 0 | 0 | 0 |
| more than seven files | 0 | 0 | 0 |
| no source file | 0 | 0 | 0 |

- **files the fix touches.** Source files that the fixed program changes against the buggy program.
- **no source file.** The fixed program equals the buggy program, so the fix lies outside the program.
- **SelfHeal received every fix file.** Runs whose input held every source file the fix touches.
- **test passed.** Runs whose repair passed the case's test.

The fix of every such case changes one source file, the program itself, and SelfHeal received it in all 135 runs. Every AgentDefect run received a single program file.

### 3.4 What each fix changed

A fix can only work when it changes the structural part that causes the failure. This subsection compares the functions each repair changed with the functions the dataset's fixed program changes.

**Table 7.** Runs with gpt-oss-120b on the 27 cases whose test fails without a fix, by whether the repair changed the functions the fixed program changes.

| repair changed | runs | test passed | successes |
|---|---|---|---|
| every function the fix changes | 115 | 18 | 18 |
| some of those functions | 19 | 6 | 6 |
| none of those functions | 0 | 0 | 0 |
| repair that does not parse | 1 | 0 | 0 |

- **function.** A top-level function, a class method, a class body or the module-level code, as the scoring script divides a program.
- **every function the fix changes.** The repair changed every function that the fixed program changes against the buggy program, and possibly other functions.
- **some of those functions, none of those functions.** The repair changed only part of those functions, or none of them.
- **test passed, successes.** As defined for Table 2.
- **repair that does not parse.** The repair is not valid Python, so its functions cannot be compared.

In 115 of the 135 runs the repair changed every function the fix changes, yet only 18 of those runs passed. Runs that changed only some of them passed in 6 of 19. At the level of whole functions, the changed parts do not separate passing repairs from failing ones. A finer record, such as the lines or calls a repair changes, is needed to find the structural part that matters.

## 4. Early signal from SelfHeal's critic on AgentDefect with gpt-oss-120b

SelfHeal's critic reviews the code of each attempt and either accepts it or asks for another attempt, up to three attempts in all. This section asks whether an early signal can lower the cost of estimating q to a given precision.

The definition of q already provides one saving. A rejected run counts as a failure, so only accepted runs need a test. On the 27 cases whose test fails without a fix SelfHeal accepted 94 runs and rejected 41. Testing only the 94 accepted runs yields the same q, 24 of 135, and saves 41 tests. An early signal has to improve on this saving.

**Table 8.** SelfHeal time and test time for the runs with gpt-oss-120b that recorded both.

| cases | runs | SelfHeal minutes per run | test minutes per run | test share of total time |
|---|---|---|---|---|
| 27 that fail without a fix | 135 | 1.59 | 0.30 | 0.158 |
| all 36 | 180 | 1.41 | 0.31 | 0.180 |

- **runs.** Runs with both a SelfHeal time and a test time on record.
- **SelfHeal minutes per run.** The time of all attempts of a run, averaged over these runs.
- **test minutes per run.** The time of the case's test, averaged over these runs.
- **test share of total time.** Test time divided by the sum of SelfHeal time and test time over these runs.

Tests take 0.158 of the total time on the 27 cases whose test fails without a fix and 0.180 on all cases, so most of the cost lies in the SelfHeal run itself.

**Table 9.** Runs with gpt-oss-120b and a result file, by the critic's verdict on attempt 1.

| cases | runs | accepted at attempt 1 | successes | rejected at attempt 1 | successes | attempt 1 share of SelfHeal time |
|---|---|---|---|---|---|---|
| 27 that fail without a fix | 135 | 76 | 20 | 59 | 4 | 0.56 |
| all with a result | 180 | 112 | 46 | 68 | 8 | 0.59 |

- **accepted at attempt 1.** The critic accepted the first attempt, which ends the run.
- **rejected at attempt 1.** The critic rejected the first attempt, and the run went on to attempt 2.
- **successes.** Runs in the column to the left that the critic accepted at some attempt and that passed the case's test.
- **attempt 1 share of SelfHeal time.** The time of attempt 1 summed over runs, divided by the time of all attempts summed over runs.

The verdict on attempt 1 arrives after 0.56 of SelfHeal's time on the 27 cases whose test fails without a fix and after 0.59 on all cases. After a rejection, attempts 2 and 3 take the remaining 0.44 and 0.41 of the time. This is the time an early signal could save. Rejected runs still hold 8 of the 54 successes, and on the 27 cases they hold 4 of the 24, three accepted at attempt 2 and one at attempt 3. Stopping every rejected run would therefore bias q, while continuing a random share of them keeps it unbiased.

Stopping SelfHeal after attempt 1 yields 46 successes in 180 runs, stopping after attempt 2 yields 51, and the full loop yields 54. Attempt 3 added three successes.

## 5. SelfHeal's early signal and two papers

### 5.1 Where an early signal helps

The design question is where to spend the expensive part of each run. Suppose the runs that receive the full outcome are chosen at random with a probability fixed in advance. A signal that disagrees with the test then costs precision and leaves the estimate unbiased.

### 5.2 Within-run randomization

Sawarni et al. (arXiv 2611.09792) randomize an intervention with a known probability at each eligible decision within a run. They let the run continue and estimate the value of a policy from those runs (§2.2 eq. 2, §2.3 eq. 5). Their ImpossibleBench study is the closest to SelfHeal. After each of the first five failed code submissions, it assigns a neutral note or adversarial feedback at random (§3.3). Their Appendix A.2 states that "When the propensity e(h) is known, the score stays conditionally unbiased even when the outcome predictions are wrong."

- **Cost.** In SelfHeal the eligible decision is a rejection at attempt 1. The run continues with a probability fixed in advance and stops otherwise, and each continued run is weighted by the inverse of that probability. This estimates the q of SelfHeal as published and skips attempts 2 and 3 in the stopped runs. Other signals from attempt 1, such as the critic's text, the files changed or a module check, enter only through the outcome model. They narrow the interval and leave the target unchanged.
- **Repair effect.** Here the intervention is the retry with the critic's feedback, and their policy gain asks whether it helps. Because stopping ends a run, the q of stopping after each attempt is already known for every recorded run without randomization (Section 4). Randomization becomes necessary when both arms continue, for example the critic's feedback against a neutral note, which mirrors their neutral and adversarial feedback.

### 5.3 Surrogate outcomes

Athey et al. (arXiv 1603.09326) conclude that surrogates "can also greatly improve the precision of estimates even in settings where the treatment effect on the long-term outcome can be estimated directly, particularly when that outcome is rare or noisy." Success with gpt-oss-120b on AgentDefect occurs in 54 of 180 runs.

- **Source of the gain.** By their Remark 7, the gain equals the outcome noise left after the surrogate index, the term with (Y − μ(S,X))², which the index removes.
- **Assumption.** When signal and outcome are observed in the same runs, their Theorem 3(ii) gives the gain from assuming surrogacy. Their Remark 9 says this gain "captures just the value of the surrogacy assumption." Surrogacy means that a configuration changes success only through the signal.
- **Fit to this study.** Surrogacy concerns a treatment, so the gain applies to a difference in q between two configurations, which is the comparison the research question requires. For the q of a single configuration, continuing a random share of rejected runs needs no such assumption.
- **Testing the assumption.** Their Remark 1 makes surrogacy testable once two configurations have full outcomes. On AgentDefect, DeepSeek-V4.1-Flash and GLM-5.3 have tested every run, so the test can start there. Their Section 3.2.3 favours several surrogates over one, so the test would combine the verdict with the critic's text and the files changed.

### 5.4 Proposed check

The following steps are proposed and have not yet been run.

- The signal is the attempt 1 verdict, and the probability of continuing after a rejection is fixed before any run. No predictor is learned.
- A resampling check on the 180 recorded runs needs no new model calls. It repeatedly draws stop or continue for each rejected run and compares the interval of the weighted q with plain subsamples of equal SelfHeal time.
- New runs with gpt-oss-120b would then follow the frozen design, and a second configuration would enter when the target is a difference in q.
- A small continuation probability widens the interval. The saving may therefore remain well below the 0.44 of the time that attempts 2 and 3 take on the 27 cases whose test fails without a fix.

## 6. Web search of SelfHeal on AgentDefect with three models

SelfHeal's fix agent searches the web through a search tool, and its critic searches the web when it verifies API usage. SelfHeal's published code places no limit on the number of searches. The fix agent is a LangGraph ReAct agent run with default settings, so its only ceiling is LangGraph's default limit of 10007 steps in our environment.

**Table 10.** Web searches by the fix agent and the critic in the AgentDefect runs of three models.

| model | searches | share that failed | median per run | most in one run | runs with a failed search | expected if each search fails independently |
|---|---|---|---|---|---|---|
| gpt-oss-120b | 541 | 0.022 | 1 | 41 | 0.08 | 0.07 |
| DeepSeek-V4.1-Flash | 3824 | 0.070 | 8 | 207 | 0.16 | 0.51 |
| GLM-5.3 | 2269 | 0.026 | 7 | 59 | 0.21 | 0.22 |

- **searches.** Replies of the fix agent's search tool and of the critic's API check in the run logs, from kept runs and from runs set aside for repetition. Runs of the earlier configuration without streamed replies are left out.
- **share that failed.** The share of searches whose reply reports a search error.
- **median per run, most in one run.** Taken over runs with at least one search.
- **runs with a failed search.** The share of runs with at least one search in which at least one search failed.
- **expected if each search fails independently.** The mean over runs of 1 − (1 − p)ⁿ, where p is the model's share of failed searches and n is the run's number of searches.

All 341 failed searches were timeouts on html.duckduckgo.com. For gpt-oss-120b and GLM-5.3, the share of runs with a failed search matches the prediction for independent failures. For DeepSeek-V4.1-Flash, failures fell in fewer runs than independence predicts, 0.16 against 0.51. A run with a failed search is repeated once, and a second failure is kept as it is.

## 7. Data and code

Every number in this report is computed from the records under `AgentDefect/SelfHeal/` and `AgentDefect/case_check/` by `docs/selfheal_agentdefect_report_numbers.py`, and its registry gives the source of each number. The success rule is in AgentDefect's `score_tests.py` line 143 and the runs of the original program in its `test_repairs.py`. The groups and causes apply the rules of AgentIssue-Bench's `analyze_multifile.py` to the AgentDefect records. SelfHeal's search tools are in its `run_agent.py` lines 204 to 229, the fix agent in lines 247 to 254 and 325 to 328, and the attempt limit in line 281. LangGraph's step limit is in `_config.py` line 31. The full list of differences from the original repository and paper, with the evidence for each, is in `docs/selfheal_deployment.md` section 5, and the project plan is `Plan_bench.md`.
