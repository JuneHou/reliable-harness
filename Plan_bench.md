# Plan_bench. Reliability of nine LLM-based harness repair methods on AgentDefect and AgentIssue-Bench

## Purpose

- Method: the RQ of the project, "How much evidence distinguishes repair effects from stochastic variation?" (Harness Literature Review artifact, tab "Boundary + method", the card labelled RQ2 there). The advisor chose it as the project's direction, and it is called the RQ from here on. The nine methods are harness papers of the review, whose section 5 states "Harness mitigation is an established target of this review. The comparison is about particular procedures and editable objects." (`docs/Agent_Error_Mitigation_Review (1).html`, section 5).
- Jun: "please read this folder to continue help me on this reliablityy measure and evaluation for stochastic harness process (LLM based)". Jun "2 and 3", choosing the reliability levels. Jun "ok, then 9 to test.", choosing the methods. Jun, giving the advisor's expectation, "can we propose a new calibrated success rate as a new measurements", "Method agnostic, no matter how they repair, they can just calculate our metric" and "We can have some causal study to find key reason why some repair success or not, and to design a better repair".

## Motivation

Each method paper's own text says the following about stochastic runs.

- RRSI repeated every search with the same base harness, evolve split, policy, round count and candidate budget, "with only the randomness of the proposer redrawn". It writes that "the evolution run is itself stochastic, and a second run from the same starting harness would follow a different trajectory", and that "What the comparison should preserve is not the identity of the accepted edits, which we do not expect to recur, but the property the regularizers are meant to produce" (App. E.2). The paragraph on its acceptance rule opens with "Repeatedly selecting among noisy evaluations can convert stochastic winners into permanent search state" (§3.3).
- DGM writes "Because the LLMs we use are inherently stochastic, performance can be noisy" (§4.2). It ran the whole method three times on Polyglot and reports the mean and the standard deviation of the accuracy (App. A.4).
- ADAS scores each agent on the ARC validation and test sets "five times to reduce the variance from the stochastic sampling of FMs" (§4.1).
- AFlow tests each generated workflow five times on the validation set and computes the mean and the standard deviation (§4, Evaluation).
- HarnessFix writes that the "non-deterministic nature of these trajectories makes traditional debugging and repair techniques substantially less effective" (§I). Its task scores are "arithmetic means over three independent runs" (§IV-D).
- ModularRSI names as a problem that trajectories must be compared "to distinguish recurring harness deficiencies from task-specific decisions or stochastic failures" (§1).
- SelfHeal writes in its threats to validity "to reduce LLM stochasticity, we compare our approach against baselines under identical settings" (§6).
- GEPA removes sampling randomness in its kernel experiments, where "generation stochasticity (temperature based sampling) is eliminated by operating under a cache" (§5.1).
- ACE has no statement about variation between runs.

Our own pilot shows that a pass can come without the repair's path running. In AgentDefect case 77178370 the published repair adds a retrieval tool. Of its nine runs with the repair, six passed and two executed the tool, so four passes came from runs that never took the repair's path. The test accepts any answer that contains the word brick, which the model gives from its own knowledge (`docs/harness_repair_motivation_report.md`, "Why the 77178370 passes mislead").

## Research framing

The RQ is "How much evidence distinguishes repair effects from stochastic variation?" Every method here calls an LLM at every step, so a finding that repairs vary between runs is expected and is the starting point, not a result. The model cannot be changed, so the study works on the program. It delivers a calibrated success rate that any repair method can compute, a causal study of the structural variables that decide whether a repair succeeds, and evidence for how many runs the rate needs. The study asks three questions in the order its experiments run, each using what the one before produced, and ends with a better repair.

| question | what is measured | design | analysis |
|---|---|---|---|
| Q1. How far is the one-run success rate from the true success rate? | the calibrated success rate per method, model and dataset, how much a one-run rate moves across the five reruns, and the success each artifact adds or removes | the baseline runs, with no new runs. Executing the original program (the unmodified buggy code, five runs, through the same path as the repairs) gives the baseline probability. The artifacts are passes without a fix, first-attempt against final-policy success under the retry rule, the search leakage audit and the model routing audit | the repair pass rate and the gain over the original with their intervals, the spread of the one-run rate across the five reruns, the points of success each artifact accounts for, per method and dataset, and the number of cases whose original program fails all five runs, where a gain over the original can show |
| Q2. Which structural variables decide whether a repair succeeds? | the causal effect of each structural variable on the pass, the pass rate under one value minus the pass rate under another, with its 95% interval | three steps in order, with new perturbation runs. Find the structural variables in our reruns, the parts that change least from run to run, meaning code paths, tools, library versions and setting values, together with whether the repair's own path ran in each passing run, read from the relay log and, where the relay log does not show it, from traced runs. Perturb them, in one fixed codebase, the original program, where only the variable changes and its value is set at random in each run with a known, equal probability on the same inputs (Sawarni et al., arXiv 2611.09792, §2.2, departure 5). Measure the causal effect (§2.4). The first case is AgentDefect 77099194, where only k, the number of rows retrieved, varies over the values its original program and its repairs use, 1, 5 and 10. Each run records whether the titles the test requires reached the model's request, read from the relay log, and whether the test passed | the effects across cases give the key reasons why repairs succeed or fail, and they guide the design of a better repair. In 77099194 they separate a retrieval change that raises the pass rate from one that delivers the evidence but leaves the model unable to use it. The calibrated success rate stays computable for methods that expose no trace |
| Q3. How many runs does the calibrated success rate need? | for each defect and model, whether the outcome over the reruns is stable (all pass or all fail) or mixed. For a repair, its pass rate against the unrepaired harness, and how often a decision built on fewer runs is wrong. For the calibrated success rate, how far its value from one run, from a fixed number of repeats and from a precision-based repeat policy falls from its value on fresh runs with a higher budget | the cheap signals are the agreement among the repairs of one defect (same files and functions changed, similar edits), the agreement of the method's own verdicts across reruns, where the repairs are located, and the defect's type, with retrieval-pipeline defects as one type (chunking, the vector store, retrieval or document metadata, 15 of the 37 AgentDefect cases, `docs/agentdefect_component_table.csv`). A subset of repairs is tested five times each (departure 4), which gives each one a pass rate to compare against. Each of these tests records the program's tool and retrieval calls. Smaller numbers of runs are drawn from those runs. The procedure is then frozen and compared against fresh runs, `[number]` per case | how well each signal predicts a stable or a mixed outcome, studied on the baseline runs of all nine methods and on held-out models. The rate of accepting a repair that does not beat the unrepaired harness, and of picking the wrong method in a comparison, against the number of runs. The estimation error, interval coverage and run cost of one run, a fixed number of repeats and the precision-based repeat policy. Set beside the evidence each method uses and the gains each paper reports |

After Q3, a better repair is designed to change the structural variables that Q2 finds decide success, and it is scored with the calibrated success rate like the nine methods.

The method follows from the answers. It is a calibrated success rate for repair methods. For each case, the success probability of a method is the probability that a fresh run of the method returns a repair that passes a fresh execution of the dataset's test, and the baseline probability is the probability that the original program passes. The rate is two numbers on one fixed case set, the repair pass rate, which is the mean over cases of the success probability, and the gain over the original, which is the mean over cases of the success probability minus the baseline probability, in percentage points. Each comes with its interval and the number of runs used. Cases count equally even when some receive more runs. A run whose method returns no repair or reports failure counts as unsuccessful, and evaluator outages are recorded apart. The rate needs only the returned repair, the original program and the dataset's test, so any repair method can compute it. It comes with the Q1 artifacts reported apart from repair effects, Q2 explains it through the structural variables, and it comes with the precision-based repeat policy that Q3 tests, which spends further runs where the Q3 signals say the outcome is unsettled. Its posteriors are the Jeffreys posteriors of `motivation/src/motivation_pilot/verdict_stats.py`. The rate, its repeat policy and the causal study are the project's own contribution, built later from the data of the current stage, which measures the baseline performance of all nine methods. No method has a special role, SelfHeal included. Jun "we are now test to collect baseline performance and data, the final acceptance rule or threshold or design is what we will self create as contribution and innovation" and "it is just one of nine like others". The repeat policy is judged by estimation error, interval coverage and run cost against one run and a fixed number of runs.

The SelfHeal runs on AgentDefect and AgentIssue-Bench (`docs/selfheal_deployment.md`) are the baseline runs of one of the nine methods, like the runs of the others. They show that SelfHeal's repairs and their test outcomes vary between reruns, that its own verdict does not predict the test, and that evaluators and run artifacts can look like repair effects. They supply data for Q1 and Q3, and their case 77099194 is the first case of Q2.

## Departures from your instruction

1. Run order. Within each batch, the with and without configurations of a comparison run in one seeded random order, not one arm after the other. Reason: the same configuration has given different pass counts in two batches of the earlier AgentDefect study (`docs/harness_repair_motivation_report.md` section 3, claim 2 row), so drift between batches would enter ΔY.
   Status: no "One version after the other"
2. Removability rule (open question B). A change is removable when, on every input, the posterior probability that removing it lowers the pass rate is at most 0.05. The model gives "no change in outcome" its own prior mass of one half, with Jeffreys Beta(0.5, 0.5) priors on the pass rates. Reason: Jun's form "a change is removable if remove ir not leads to decrease in performance or turn from success to failure of outcome. Or, remove the repair shows no change to outcome.". The prior mass of one half is my choice.
   Status: no "No". The replacement rule is asked as its own question.
3. Case pool. AgentDefect: 36 of the 37 folders. Folder `hf-26` holds `run_fixed.py`, `test.py`, `readme.md` and `requirements.txt` but no `run_buggy.py`, so there is no broken harness for a method to repair. AgentIssue-Bench: all 50 issues enter the check of each defect case. For 14 of them (autogen_4733, autogen_4785, autogen_4197, autogen_5007, camel_1145, autogen_3361, camel_1273, metagpt_1313, camel_1614, autogen_1844, chatdev_318, chatdev_413, chatdev_465, sweagent_741) our earlier inspection recorded no entrypoint modes and no reproduction script, because their images are built only for arm64 (`entrypoints.json` status `platform_unsupported`), so their images are inspected again first. An issue whose authors' test cannot be run on a patched tree is reported as not runnable. For `haystack_8912` the authors' own test replaces the model call (`fake_prepare_api_call`), which Jun's rule forbids. How to treat it was asked separately.
   Status: no "you might wrong. why no buggy in the dataset. agentissue bench all 50". AgentIssue-Bench enters with all 50 issues.
4. Repeated tests for Q3. A subset of repairs, every repair of five defects with mixed outcomes and of five defects drawn at random from the others, per method, model and dataset, is tested five times each with the dataset's test, so each has a pass rate to compare smaller numbers of runs against. Every other repair keeps one test. Reason: Q3 needs a pass rate per repair, which one test cannot give. This reverses "yes, each tested once" for that subset.
   Status: yes "numbers will be five", giving the numbers of this departure For `hf-26`, the released archive is identical to the official repository's `AgentDefect.zip` (git blob ae5b4f3d), it lacks `run_buggy.py` although the folder's readme says to run it, and SelfHeal's `Detailed Result.xlsx` lists `hf-26`, so the authors had a buggy program that the release omits. How to obtain it is asked as its own question.
5. Q2 run order. In Q2 the value of the perturbed variable is set at random in each run with a known, equal probability, as Sawarni et al. assign interventions (§2.2), and not one value after the other as the decision "run order" says. Reason: the random assignment is what makes the Q2 effect causal (§2.4), and the same configuration has given different pass counts in two batches of the earlier AgentDefect study (`docs/harness_repair_motivation_report.md` section 3, claim 2 row), so a drift between batches would enter the effect if one value ran after the other.
   Status: awaiting written yes

## Instruction

- Jun "write delivery in Plan_bench.md. 1. option two. 2. collect what they used in paper to a table first. including ablation. 3. to be determined"
- Jun "for 3, user [number] as placeholder when write plan. this will be more then 1 so doesn't matter"
- Jun "I remember you said severak papers mentioned the stochatic and none replicable of same repair as limitation, can you remind me which? and add this as motivation in the Plan_bench"
- The options Jun answered (my message). Option two: "our two datasets. That needs an adapter per method, since only SelfHeal was built for AgentDefect." Decision 2: "Which model each method uses. Either the model in its own paper, or one common model for all nine." Decision 3: "How many times each method is rerun on the same starting harness, and the overall budget."
- Terms a builder could read two ways, each with its definition source.
  - method → one of the nine published methods: HarnessFix, SelfHeal, ModularRSI, RRSI, GEPA, ACE, DGM, ADAS, AFlow. Jun "ok, then 9 to test."
  - reliability → two things. How much a method's repairs vary when it is rerun on the same defect, and whether the changes a method keeps hold up when each is tested with and without it. Jun "2 and 3", answering the second and third of three options in my message. The second option: "Run the same method ... on the same defect several times ... how often its repairs succeed and how much they differ". The third option: "Each method accepts a repair after one or a few passing runs ... how often a method accepts a repair whose effect is not established, or keeps a change that is removable."
  - what they used in paper → the models each paper reports, in every role it names. Jun "collect what they used in paper to a table first"
  - ablation → every experiment row the paper reports beyond its main setting, kept under the paper's own label, none dropped. Jun "including ablation"
  - [number] → a count not yet chosen, written literally as `[number]`. Jun "use [number] as placeholder"
  - Plan_bench.md → `/data/wang/junh/githubs/stochastic-harness/Plan_bench.md`. Jun "write delivery in Plan_bench.md"
- Jun "please rename RQ2 as the RQ, and rethink 3 contribution since advisor chose RQ2 as major direction"
- Jun "everyone know LLMs are stochastic. so we need deeper insights and findings from carefully designed experiments", then "not an available question "Which stage creates the variation?" when LLM used", then "this sounds adaptable. current experiments are motivations, correct?", "and for further test and analysis to get findings and develop method" and "can you update the plan document?"
- Jun "the repair is generated once as a whole piece, you cannot break them"
- Jun "please update", answering four proposed edits. The retrieval case 77178370 in the Motivation, retrieval-pipeline defects as one defect type in Q1, the trace of whether the repair's own path ran in Q3, and the tool and retrieval calls recorded in the Q2 repeated tests for the decision "unit of Y"
- Jun, giving the advisor's expectation of the project's goal and delivery: "Calibrated evaluation metrics, if people just run it once, just calculate success rate, that might no the the true success rate, can we propose a new calibrated success rate as a new measurements. — structural variable? Method agnostic, no matter how they repair, they can just calculate our metric. We can have some causal study to find key reason why some repair success or not, and to design a better repair."
- Jun "thisi s build upon she agree our structural variable finding and then pertubation"
- Jun "so the sequence is, we find the structural variable, from our rerun which change least, then we do pertubation on these, then we measure causal effects. this is what i mean"
- Jun "can you adopt what you feel can improve our plan thenupdate the plan? now we have m uch clear target", after my feedback on a proposal Jun pasted. Adopted from it: the score of its point 1, the test of the procedure in its point 2, and the 77099194 experiment of its point 3 with random assignment in place of interleaving. Not adopted: running the developer fix, which Jun dropped ("i don't trust your generate results of set 2. drop all"), and reporting shipped and corrected AgentIssue-Bench results side by side, since the fix plan reports the shipped evaluator's records only (Jun "you should never change evaluation code or file to make result incomparable")
- Jun "agree", to ordering the questions as the experiments run. Q1 is the calibrated success rate from the baseline runs, Q2 the structural variables and their causal effects, Q3 the number of runs, then a better repair. Lines above that name Q1 to Q3 use the earlier numbering, where the earlier Q1 (cheap signals) and Q2 (repeated tests) are now in Q3, and the earlier Q3 (artifacts) is now in Q1

## References read

- `docs/Agent_Error_Mitigation_Review (1).html`: section 5 (one line per paper on what it evaluates), section 11 (repository audit, "environment not run" for every repository), section 6 model fields for HarnessFix, SelfHeal, ModularRSI and RRSI.
- `docs/advisor_check_4q.md`: Q1 and Q2 columns of the 21-paper table, which say each of the nine proposes its change with an LLM (ADAS row says "meta agent").
- The nine papers, read for the table of models each paper used, by three reader agents, each returning a verbatim quote per row. One row per paper was then confirmed against the paper text. Papers are https://arxiv.org/abs/2606.06324 (HarnessFix), https://arxiv.org/abs/2604.17699 (SelfHeal), https://arxiv.org/abs/2609.14857 (ModularRSI), https://arxiv.org/abs/2609.24972 (RRSI), https://arxiv.org/abs/2507.19457 (GEPA), https://arxiv.org/abs/2510.04618 (ACE), https://arxiv.org/abs/2505.22954 (DGM), https://arxiv.org/abs/2408.08435 (ADAS), https://arxiv.org/abs/2410.10762 (AFlow). Checked: every model the paper names, by role and experiment, with its section or table.
- The arXiv HTML pages of the nine papers, for the Motivation section: https://arxiv.org/html/2606.06324v2 (HarnessFix), https://arxiv.org/html/2604.17699v1 (SelfHeal), https://arxiv.org/html/2609.14857v2 (ModularRSI), https://arxiv.org/html/2609.24972v3 (RRSI), https://arxiv.org/html/2507.19457v2 (GEPA), https://arxiv.org/html/2510.04618v3 (ACE), https://arxiv.org/html/2505.22954v3 (DGM), https://arxiv.org/html/2408.08435v2 (ADAS), https://arxiv.org/html/2410.10762v4 (AFlow). Each was searched for stochastic, nondeterministic, noise, variance, fluctuation, seed, repeated runs, reproducibility and confidence interval. Each hit was read in its section, and the section label was taken from the page headings. ACE gave no hit about variation between runs.
- https://arxiv.org/html/2609.14857 (ModularRSI) section 3.2 and appendix B: modules and their interfaces.
- `/data/wang/junh/githubs/SelfHeal/AgentDefect.zip`: 37 case folders, 36 with buggy, fixed and test files, `hf-26` without `run_buggy.py`.
- `/data/wang/junh/githubs/AgentIssue-Bench/motivation_experiment/artifacts/agentissue/entrypoints.json`: 50 issues, 36 with `apply_patch` and `test_patched` modes.
- `/data/wang/junh/githubs/AgentIssue-Bench/motivation_experiment/artifacts/agentissue/repro/haystack_8912.py`: patches the OpenAI call with `fake_prepare_api_call`.
- `motivation/src/motivation_pilot/verdict_stats.py`: `LEVEL = 0.95`, Jeffreys posteriors, `prob_delta_below`.
- `~/.claude/CLAUDE.md` section "No fake model calls and no unlabelled hypothetical numbers".
- `env` of this shell: no OPENAI, ANTHROPIC, OPENROUTER or GOOGLE key is set.

## Baseline

Anything this plan does not name stays identical to `/data/wang/junh/githubs/stochastic-harness`.

## Inventory

Built from `find /data/wang/junh/githubs/stochastic-harness -maxdepth 1` and `git status --short`.

| file | action | note |
|---|---|---|
| `Plan_bench.md` | create | this plan with dates removed, plus the table of models each paper used |
| `docs/NUMBERS.md` | modify | one row per number in `Plan_bench.md` |
| `CLAUDE.md` | unchanged | |
| `motivation/` | unchanged | |
| `docs/` other files | unchanged | |
| `.gitignore` | unchanged | |

## Decisions

| decision | value | source |
|---|---|---|
| where the methods run | AgentDefect and AgentIssue-Bench, with code for each method that feeds it our cases and collects its repair | Jun "1. option two" |
| methods | HarnessFix, SelfHeal, ModularRSI, RRSI, GEPA, ACE, DGM, ADAS, AFlow | Jun "ok, then 9 to test." |
| reliability measured | how much a method's repairs vary when it is rerun on the same defect, and whether a repair the method accepts holds up against the unrepaired harness, the repair tested as a whole | Jun "2 and 3", then "the repair is generated once as a whole piece, you cannot break them" |
| questions and method | Q1 to Q3 in the order the experiments run and the calibrated success rate of the section Research framing, in place of the earlier acceptance rule | Jun "this sounds adaptable", "and for further test and analysis to get findings and develop method", then the advisor's expectation and Jun "can you adopt what you feel can improve our plan thenupdate the plan? now we have m uch clear target" |
| success in the calibrated success rate | a fresh run of the method returns a repair that passes a fresh execution of the dataset's test. No repair, or a method reporting failure, counts as unsuccessful. Evaluator outages are recorded apart. Cases count equally | Jun "failed just count to wrong", and the adopted point 1 |
| structural variables (Q2) | the parts that change least from run to run in our reruns, meaning code paths, tools, library versions and setting values | Jun "so the sequence is, we find the structural variable, from our rerun which change least, then we do pertubation on these, then we measure causal effects" |
| codebase perturbed in Q2 | the original program, so that no repair is split | Jun "the repair is generated once as a whole piece, you cannot break them" |
| assignment in Q2 | the variable's value set at random in each run with a known, equal probability | departure 5 |
| first Q2 case | AgentDefect 77099194, k only, over 1, 5 and 10, with the required titles in the model's request read from the relay log, and the test's pass | the adopted point 3, and the case's records in `docs/selfheal_agentdefect_report_numbers.md` |
| role of the SelfHeal runs | baseline runs of one of the nine methods, like the others | Jun "we are now test to collect baseline performance and data" and "it is just one of nine like others", replacing "current experiments are motivations, correct?" |
| model per method and role | every method and every role runs on three VT ARC models in turn, gpt-oss-120b first, then GLM-5.3, then DeepSeek-V4.1-Flash, through `https://llm-api.arc.vt.edu/api/v1` | Jun "let's use free arc api supported model for rerun now." Jun "all 3. gpt-oss-120b first, then GLM-5.3 then deepseek" |
| embedding model | none chosen. SelfHeal uses none, and it never runs the programs (`docs/selfheal_workflow.md` section 4). The 14 AgentDefect programs that embed keep their own code unchanged when their test runs | Jun "no embedding model as you siad. drop." |
| embedding store | each OpenAI embedding request is saved with OpenAI's reply, keyed by the exact request body (model and input). A later identical request reuses the saved reply. Any other request is a real OpenAI call, and its reply is added. Each run records which embedding replies were reused and which were called | Jun "i forbidden fake LLM. this is saved from real run". Jun "let's use open ai get those embedding, and call open ai embedding at real time as well" |
| method repeats per case | five, with each ARC model | Jun "five times", answering how many times SelfHeal is rerun on each case |
| test runs per returned repair | one, except the Q3 subset of departure 4. Jun's "five times" answered the number of reruns | Jun "yes, each tested once", then "i see no difference or changes from new answer" |
| runs of the check of each defect case | five for the buggy code and five for the fixed code, for methods whose own steps run the harness. SelfHeal has no such step, since "SelfHeal does not execute code during debugging" (SelfHeal paper §4.4), so no case check is run as part of SelfHeal. Executing the original program, the step "Execute the original program", is a separate check and runs for every case of both datasets, whatever the method | Jun "for 4, isn't i already said 5?", then "if no, why you ask me. rethink". Jun "now. fix everything you didn't follow the plan" |
| SelfHeal run | for each ARC model in turn, the steps of SelfHeal §3 and nothing else. Build the fix rules (§3.1), rebuild the missing code intents as a recorded dataset input (§4.2), then run the fix agent and critic loop (§3.2) on all 37 cases, five reruns per case. No AgentDefect program is run | SelfHeal paper §3, §4.4. Jun "if no, why you ask me. rethink" |
| experiment folder layout | `<dataset>/<method>/<model>/<case>/rerun_<k>/` under this repository, each rerun folder holding SelfHeal's own `result.txt`, the test run of its repair and the relay log. Files shared by all cases sit one level up, `<dataset>/<method>/inputs/` and `<dataset>/<method>/<model>/rules/`. The check of each defect case, which does not depend on the method, is `<dataset>/case_check/<model>/<case>/`. The rebuilt AgentIssue-Bench images are `AgentIssue-Bench/images_amd64/` | Jun "the experiment should under <dataset>/<method>/<case>", then "we should add another <model> level" |
| model calls of SelfHeal and of the AgentDefect programs | a relay on this machine receives every OpenAI-style request, sends chat requests to ARC with the model name replaced by the run's ARC model and embedding requests to OpenAI with `institutional.sh`, and saves each request with its real reply. No code file is edited | Jun "1. ok", after "what is relay" |
| model for building SelfHeal's fix rules and intents | the same ARC model as the run, through the relay. `extract_summary.py` and `make_rules.py` run unchanged in an environment with openai 0.28.1, because their call `openai.ChatCompletion.create` (`extract_summary.py:63`, `make_rules.py:50`) does not exist under SelfHeal's pin openai 2.14.0 | Jun "if this is part of the repair, should use same model as arc model" |
| runs per configuration, budget | five | Jun "numbers will be five" |
| model replacement | none in any run, check or test; a run counts only when it records a real completion | Jun "fobidden the use of any fake LLM" |
| "contributes" | superseded, the repair is tested as a whole against the unrepaired harness, not split into changes. Earlier value: posterior P(pass rate with X > pass rate without X) ≥ 0.95 for a change X in a repair, with the rest of the repair held fixed, no minimum effect size | Jun "A. no change", then Jun "the repair is generated once as a whole piece, you cannot break them" |
| "removable" | superseded, the repair is tested as a whole against the unrepaired harness, not split into changes. Earlier value: X is removable when, on every input, the `[number]` runs with X pass no more often than the `[number]` runs without X. The four conditions each describe X against not having X (no change in result, a decrease in performance, an input that passes without X failing with X, failure staying failure); in all four X does not help. "Unresolved" is every change that is neither contributes nor removable, so the three labels cannot overlap | Jun "when remove X, nochange to result, or decrease in performance, or success turn failure, or failure stay failure, 4 conditions show the removable", then Jun "the repair is generated once as a whole piece, you cannot break them" |
| unrepaired harness passing on rerun | logged as self-recovery, no repair needed for that input | Jun "D. if no error in rerun. it is correct. nothing need repair. record self-recovery." |
| module | ModularRSI's five modules, retrieval and indexing under Tool Use | Jun "everything under Tool" |
| unit of Y | one final Y per complete task execution. In the SelfHeal runs, the Q3 repeated tests record the program's tool and retrieval calls with each Y, and the relay log keeps every model call | Jun "Record final Y per complete task execution, with linked module invocations and boundary observations." Jun "please update", answering the four edits that add the retrieval case |
| AgentIssue-Bench cases | all 50 issues enter the check of each defect case | Jun "agentissue bench all 50" |
| AgentDefect cases | all 37 folders; `hf-26` with a rebuilt `run_buggy.py`. 79776520 needs a Google key and a Tavily key, which we do not have, and is left out of the score tables with its tests kept on record | Jun "Rebuild from the forum post". Jun "for question 2, drop" |
| how `hf-26/run_buggy.py` is rebuilt | start from the archive's `hf-26/run_fixed.py`; replace its `HuggingFaceEndpoint(...)` call with the forum post's call (`repo_id="huggingfaceh4/zephyr-7b-alpha"`, `task="text-generation"`, `temperature=0.5`, `max_new_tokens=1024`); delete `llm = ChatHuggingFace(llm=llm)`; replace `chat_prompt_2` with `retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")` as the forum post's chain uses; keep every other line; record the file as our reconstruction with the diff against `run_fixed.py` | Jun "Rebuild from the forum post"; the forum post discuss.huggingface.co topic 145964 |
| `haystack_8912` | the authors' mock is retained and the evaluator branches are corrected, as in departure 5 of the SelfHeal fix plan. An earlier value removed `fake_prepare_api_call` | Jun "Remove the fake call", then "Run original test" and the correction "mock retained; evaluator branches corrected" |
| run order | within each batch, all runs with change X, then all runs without X | Jun "One version after the other" |
| dates in `Plan_bench.md` | none | baseline `CLAUDE.md` |
| model names | the exact name the paper or code gives, date part included. Where the source gives no dated name, the undated name | Jun "yes. if not available, drop", answering whether `gpt-4o-2024-05-13` keeps its date part |
| web search inside SelfHeal | DuckDuckGo through the `ddgs` package, in place of SerpAPI. Up to five results, title and snippet kept, stackoverflow.com links dropped, as in `run_agent.py:31` to `:69` | Jun "2. yes", after "i don't want to get new API. web search should be free" |
| OpenAI key for the embedding calls the AgentDefect programs make when their test runs | `/data/wang/junh/.cache/keys/institutional.sh` | Jun "3. yes" |
| AgentIssue-Bench images built only for arm64 (14 issues) | rebuilt for linux/amd64 from each image's own build steps on `python:3.10.18-trixie`, with the two scripts taken from the image's layers. Build files, logs and records in `AgentIssue-Bench/images_amd64/<tag>/`, images named `agentissue-bench-amd64:<tag>` | Jun "if able to change to x64 change if not tell me why not" |
| numbers in `Plan_bench.md` | each registered in `docs/NUMBERS.md` and checked | baseline `CLAUDE.md` |

## Table of models each paper used

"Model that makes the repair" means the model that diagnoses, proposes, edits, critiques or accepts a change. "Model inside the harness" means the model that runs inside the harness to do the benchmark tasks. "Not stated" means the paper names no model there. Experiment names are the paper's own. Rows come from the reader agents' reports with their verbatim quotes. Rows marked "inferred" are the reader's inference, not the paper's statement.

| method | experiment | model that makes the repair | model inside the harness | decoding stated | source |
|---|---|---|---|---|---|
| HarnessFix | RQ1 main, default model | GPT-5 mini (all four agents) | GPT-5 mini | not stated | §IV-D, Tables III and IV |
| HarnessFix | RQ1 main, other models | not stated | Claude Sonnet 4.5, DeepSeek V3.2, Qwen3.5 Plus, Gemini 3 Pro | not stated | §IV-D, Table III |
| HarnessFix | RQ1 baselines (GEPA, SCOPE, ReCreate, Meta-Harness, human harnesses) | GPT-5 mini | GPT-5 mini | not stated | §V-A, Table IV |
| HarnessFix | RQ3 ablation (prompt-only repair, w/o trace-grounded diagnosis, w/o scoped repair operators, w/o regression-aware acceptance) | not named, GPT-5 mini inferred | not named, GPT-5 mini inferred | not stated | §V-C, Table VI |
| HarnessFix | RQ4 cross-model transfer, GAIA, no new repair | GPT-5 mini (repair source) | Qwen3.5 Plus, DeepSeek V3.2, Gemini 3 Pro, Claude Sonnet 4.5 | not stated | §V-D, Table VII |
| SelfHeal | RQ5 main | backbone of fix agent and critic agent: Claude Sonnet 4, Gemini 3 Pro, GPT-5.2 | model called by the AgentDefect programs: not stated | not stated | §4.1, §4.3.1, Tables 1 and 2 |
| SelfHeal | RQ7 ablation (No Fix Rules, No Web Search, No Critic Agent) | Gemini 3 Pro | not stated | not stated | §4.3.3, Table 2 |
| SelfHeal | RQ8 baselines | zero-shot: GPT-5.2, Gemini 3 Pro, Claude Sonnet 4. SWE-Agent: GPT-5.2 | not stated | not stated | §4.3.4, Tables 1 and 2 |
| SelfHeal | fix-rule generation and code intent (offline inputs) | GPT 5 Mini | none | not stated | §3.1, §4.2 |
| ModularRSI | §6.1 main | Code-Modify Agent: DeepSeek-V4-Flash-Preview | DeepSeek-V4-Flash-Preview | not stated | §5.3, §6.1, Table 1 |
| ModularRSI | §6.2 cross-model, harness frozen | DeepSeek-V4-Flash-Preview | GLM-5.2, MiniMax-2.5, DeepSeek-V4-Flash | not stated | §6.2, Table 2 |
| ModularRSI | App. D different evolution models | DeepSeek-V4-Flash-Preview, DeepSeek-V4-Flash-0731, Qwen3.8-Max | not stated, same as the model that makes the repair, inferred | not stated | App. D, Table 8 |
| ModularRSI | §6.3 strategies, single-module evolution, §6.4 ablation (w/o CTA, w/o FLM, w/o VG), §6.5 baselines (AHE, Meta-Harness), §6.6 scaling | DeepSeek-V4-Flash-Preview (§6.3 and §6.4 by the §5.3 default) | DeepSeek-V4-Flash-Preview | not stated | Tables 3 to 6, Fig. 2 |
| ModularRSI | Function Merge, Task-Aware Function Composer | "an LLM", not named | not named | not stated | §3.7 |
| ModularRSI | evaluation only | judge: Opus-4.8. Difficulty labels: MiniMax M2.7, GLM-5.2, DeepSeek-V4-Pro, DeepSeek-V4-Flash | none | not stated | App. M, App. L |
| RRSI | main, three domains | proposer, analyst and leakage critic: Claude Opus 4.8 | policy: Claude Opus 4.8 | not stated | §4.1, App. E.1 |
| RRSI | baselines (Meta-Harness, AHE, TTHE, HarnessX) | not stated | Claude Opus 4.8 | not stated | §4.1, Table 1 |
| RRSI | regularizer ablation, cost analysis, second search run | unchanged from main | unchanged from main | not stated | §4.3 Table 2, Fig. 4, App. E.2 Table 7 |
| RRSI | policy robustness, coding | not stated for the Gemini run | Claude Opus 4.8, Gemini 3.5 Flash | not stated | §4.3, Table 3 |
| RRSI | cross-model transfer, no search | harness evolved with Gemini 3.5 Flash policy | Gemini 3.1 Flash Lite | not stated | §4.3, Table 4 |
| RRSI | evaluation only | judges: Gemini-3.5-Flash. JobBench: Gemini-3.5-Flash with Claude Opus 4.8. GDPval: Qwen3.6-35B-A3B, Claude Sonnet 4.6, Gemini-3.1 Pro | none | not stated | App. B |
| GEPA | main, Table 1 | reflection LM not named. Call counts are listed under the model inside the harness, same model inferred | Qwen3-8B | temperature 0.6, top-p 0.95, top-k 20 | §4, App. E.1, E.2, App. N |
| GEPA | main, Table 2 | reflection LM not named, same as the model inside the harness, inferred | gpt-4.1-mini-2025-04-14 | temperature 1.0 | App. E.2 |
| GEPA | cross-model transfer, GEPA-Qwen-Opt | Qwen3-8B | GPT-4.1-Mini at evaluation | as above | Table 2 |
| GEPA | baselines MIPROv2, TextGrad, Trace | GPT-4.1-Mini | GPT-4.1-Mini | as above | Table 2 |
| GEPA | GRPO baseline | none | Qwen3-8B, trained | training temperature 1.0 | App. E.4 |
| GEPA | ablation candidate selection, Merge | unchanged | Qwen3-8B, and both models for Merge | as above | Table 3, Obs. 5, App. J |
| GEPA | inference-time search NPUEval, KernelBench | not stated separately | GPT-4o | cached, no sampling | §5.1 |
| GEPA | adversarial prompt search | not stated | GPT-5 Mini at evaluation | not stated | §5.2 |
| ACE | main AppWorld, Finance | Reflector and Curator: DeepSeek-V3.1, non-thinking | Generator: DeepSeek-V3.1, non-thinking | not stated | §4.2, Tables 1 and 2 |
| ACE | extra domains DDXPlus, BIRD-SQL | DeepSeek-V3.1-671B | DeepSeek-V3.1-671B | not stated | App. A.2 |
| ACE | cross-LLM, all three roles switched | GPT-OSS-120B, GPT-5.1, Llama-3.3-70B-Instruct | same as the model that makes the repair | not stated | §4.5, App. A.1, Tables 5 to 9 |
| ACE | ablation Table 3, incremental update, hyperparameters | DeepSeek-V3.1 | DeepSeek-V3.1 | not stated | §4.6, App. A.5, A.6 |
| ACE | Reflector swap | Reflector: GPT-OSS-120B, DeepSeek-V3.1-671B, GPT-5.1. Curator: DeepSeek-V3.1 | DeepSeek-V3.1 | not stated | App. A.4, Table 16 |
| ACE | harmful reflector | not stated | not stated | not stated | App. A.4, Table 17 |
| ACE | baselines ICL, MIPROv2, GEPA, DC-CU | optimizer model not stated | DeepSeek-V3.1 | not stated | §4.2 |
| ACE | evaluation only | judge: GPT-4o-mini (BIRD-SQL) | none | not stated | §4.1 |
| DGM | main, SWE-bench | self-modification: Claude 3.5 Sonnet (New). Diagnosis: o1 | Claude 3.5 Sonnet (New) | temperature 1.0, all models | §4.1, App. C.3, D.1 Table 3 |
| DGM | main, Polyglot | self-modification: Claude 3.5 Sonnet (New). Diagnosis: o1 | o3-mini | temperature 1.0, all models | §4.1, App. C.3, D.1 Table 3 |
| DGM | ablations w/o self-improve, w/o open-ended exploration, Greedy | not stated | not stated | not stated | §4.3, App. A.1, A.3 |
| DGM | model transfer, SWE-bench | none | Claude 3.7 Sonnet, o3-mini | not stated | §4.4, Fig. 4 |
| DGM | model transfer, Polyglot | none | Claude 3.5 Sonnet (New), Claude 3.7 Sonnet | not stated | App. A.2, Fig. 7 |
| DGM | stability study, benchmark and language transfer | not restated | not restated | not stated | §4.4, App. A.4 |
| ADAS | main, ARC and reasoning (DROP, MGSM, MMLU, GPQA) | meta agent: "GPT-4" in the main text, gpt-4o-2024-05-13 in App. D and E | gpt-3.5-turbo-0125 | task default temperature 0.5. Meta agent not stated | §4.1, §4.2, App. C, D, E |
| ADAS | model transfer, ARC, no new search | none | claude-3-haiku-20240307, gpt-4o-2024-05-13, claude-3-5-sonnet-20240620 | not stated | §4.3, Table 3, App. A |
| ADAS | domain transfer, initialization ablation | not stated | not stated | not stated | §4.3 Tables 2, 4, 5. App. I Table 6 |
| AFlow | main, six benchmarks | optimizer: Claude-3.5-sonnet | executor: GPT-4o-mini-0718 | temperature 0, except DeepSeek-V2.5 at 1 | §5.1, Table 1 |
| AFlow | executors listed | none | DeepSeek-V2.5, GPT-4o-mini-0718, Claude-3.5-sonnet-0620, GPT-4o-0513 | as above | §5.1 |
| AFlow | ADAS baseline rerun | Claude-3.5-sonnet | GPT-4o-mini | not stated | §5.1 |
| AFlow | model transfer and cost, HumanEval | Claude-3.5-sonnet | search: GPT-4o-mini or DeepSeek-V2.5. Test: GPT-4o-mini, DeepSeek-V2.5, GPT-4o, Claude-3.5-sonnet | as above | §5.2, Table 2, App. D |
| AFlow | operator ablation | not stated | not stated | not stated | §5.2, Fig. 5 |
| AFlow | open-ended tasks | Claude-3.5-sonnet. Judge: GPT-4o | Claude-3.5-sonnet or GPT-4o-mini | not stated | App. F |

Facts from the table of models each paper used that bear on the choice:
- None of the nine papers ablates the model that makes the repair, except the ACE Reflector swap and the ModularRSI App. D evolution-model study.
- The model that makes the repair and the model inside the harness are the same model in the main runs of HarnessFix, ModularRSI, RRSI and ACE, and GEPA by inference. They differ in DGM, ADAS and AFlow.
- SelfHeal never runs the AgentDefect programs ("SelfHeal does not execute code during debugging", §4.4), and its paper names no model for them.

## The benchmark after the table of models

Each step starts only after Jun's written yes to its own plan revision.

| step | what happens | stops for |
|---|---|---|
| Read each method's code | for each method, clone its repository read-only, record the commit, its entry point, what it takes as input, where it proposes a change, where it accepts one, how it calls its model | Jun approves, per method and dataset, a written description of how the method is run on our cases |
| Execute the original program | with the chosen model inside the harness and a real key, five runs of the unmodified buggy code through the same path as the repairs. The developer fix is not run, Jun "i don't trust your generate results of set 2. drop all". Mixed outcomes are reported as they are, no case is dropped and no assertion is changed | Jun reviews the table of the original program's runs |
| Rerun each method on each case | each method runs five times on each case from the same starting harness, each run with real model calls. Record each repair, the files it changes, whether the method accepts it, and whether it passes the dataset's test. A planned repetition gets at most one replacement | none |
| Q1 calibrated success rate | from the baseline runs and the runs of the original program, the repair pass rate and the gain over the original program per method, model and dataset, with intervals, the spread of the one-run rate across the five reruns, and the passes without a fix, retry, leakage and model routing artifacts, per method and dataset | Jun reviews the table and the findings |
| Q2 causal study | find the structural variables in the reruns, perturb them, measure their causal effects, starting with 77099194 | Jun approves this step's own plan revision, which fixes the number of runs, and Jun's answer on departure 5 |
| Q3 number of runs | the agreement signals of each defect against the stability of its outcome, studied on the baseline runs of all nine methods and on held-out models. The subset of departure 4, five tests per repair, and the error curve against the number of runs. Then the procedure is frozen, and one run, a fixed number of repeats and the precision-based repeat policy are compared against fresh runs, `[number]` per case, on estimation error, interval coverage and run cost | Jun's yes to departure 4, and Jun approves the frozen procedure and the number of fresh runs before any run |
| Compare the methods | per method, the calibrated success rate, how often reruns succeed and how much the repairs differ, the share of accepted repairs whose effect is not established against the unrepaired harness, and the Q1 artifacts | Jun reviews the tables |
| Design a better repair | a repair designed to change the structural variables that Q2 finds decide success, scored with the calibrated success rate like the nine methods | Jun approves this step's own plan revision |
