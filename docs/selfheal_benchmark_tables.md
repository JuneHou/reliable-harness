# SelfHeal against the published benchmarks

Each table below is the published table as it appears in its paper, with our SelfHeal rows added at the bottom.

## 1. AgentDefect

**Table 1.** Performance comparison of bug identification and repair using different approaches. SelfHeal paper (arXiv 2604.17699) Table 2, with our three rows added.

| App. | M. | Repair | Line | Fn. | Comp. | Attmp. |
|---|---|---|---|---|---|---|
| SWE-A | GPT-5.2 | 0.3784 | 0.4865 | 0.7297 | 0.8108 | 3.78 |
| Zero-shot | GPT-5.2 | 0.3243 | 0.4865 | 0.5946 | 0.6486 | 1.00 |
| | Gemini 3 Pro | 0.3514 | 0.5135 | 0.7838 | 0.8108 | 1.00 |
| | Claude Sonnet 4 | 0.4054 | 0.5946 | 0.7838 | 0.8649 | 1.00 |
| NFR | Gemini 3 Pro | 0.4054 | 0.5676 | 0.7568 | 0.8919 | 1.30 |
| NWS | Gemini 3 Pro | 0.4595 | 0.5135 | 0.8378 | 0.8649 | 1.24 |
| NCA | Gemini 3 Pro | 0.5135 | 0.7297 | 0.8378 | 0.9189 | 1.32 |
| SelfHeal | GPT-5.2 | 0.5405 | 0.6486 | 0.7838 | 0.8919 | 1.35 |
| | Gemini 3 Pro | 0.5946 | 0.7297 | 0.8378 | 0.9189 | 1.32 |
| | Claude Sonnet 4 | 0.5676 | 0.7297 | 0.7838 | 0.8919 | 1.05 |
| SelfHeal (ours) | gpt-oss-120b | 0.2919 | n/a | n/a | n/a | 1.69 |
| | DeepSeek-V4.1-Flash | 0.4595 | n/a | n/a | n/a | 1.05 |
| | GLM-5.3 | 0.4595 | n/a | n/a | n/a | 1.05 |

Notes. App.: Approach; M.: Model; Fn.: Function; Comp.: Component; Attmp.: attempts; SWE-A: SWE-Agent; NFR: No fix rules; NWS: No Web Search; NCA: No Critic Agent. The first ten rows are copied from the paper.

- **Repair, our rows.** Share of the 37 cases in which the critic accepted the repair and the case's test passed when the repair was executed, mean over five runs. Two standard deviations over the runs are 0.1040, 0.1147 and 0.0662. The paper reports one run per case and does not state its rule for a resolved case.
- **Line, Fn., Comp., our rows.** Not computed, because the paper does not define these measures.
- **Attmp., our rows.** Mean number of attempts per run.

## 2. AgentIssue-Bench

**Table 2.** Overall results of SE agents on AgentIssue-Bench. AgentIssue-Bench paper (arXiv 2505.20749) Table 2, with SelfHeal added.

| SE Agent | LLM | Plausibly resolved% | Correctly resolved% | Localization % File-level | Localization % Function-level | Avg. $Cost |
|---|---|---|---|---|---|---|
| Agentless | GPT-4o | 12.00 | 3.33 | 27.82 | 12.99 | 0.65 |
| | Claude-3.5-S | 12.00 | 4.00 | 27.35 | 17.50 | 0.33 |
| AutoCodeRover | GPT-4o | 7.33 | 1.33 | 22.07 | 14.77 | 0.23 |
| | Claude-3.5-S | 12.67 | 4.67 | 25.81 | 19.18 | 0.05 |
| SWE-agent | GPT-4o | 0.67 | 0.67 | 11.67 | 4.22 | 1.15 |
| | Claude-3.5-S | 2.00 | 2.00 | 9.52 | 6.78 | 0.57 |
| SelfHeal (ours) | gpt-oss-120b | 20.00 | n/a | n/a | n/a | n/a |

Notes. The first six rows are copied from the paper. Each paper row is the mean over three runs on the 50 issues.

- **Plausibly resolved%, our row.** Percent of the 50 issues whose patch makes the issue's test pass, scored through the benchmark's own test path and pass rule, mean over our runs 1 to 3 as the paper uses three runs. SelfHeal's patch is the code it returns, whatever its critic decided. Two standard deviations over the three runs are 8.00. Over all five runs the mean is 18.80 with two standard deviations of 6.69. In our runs the original code already passes the test in 10 issues, and 41 of SelfHeal's 47 passing runs fall in those issues.
- **Correctly resolved%, our row.** Not measured. It needs two human reviewers to compare each passing patch with the developer's patch.
- **Localization, our row.** Not computed. The paper does not say whether every changed file or function must match the developer's patch or only one.
- **Avg. $Cost, our row.** Not comparable, because ARC charges nothing.

DeepSeek-V4.1-Flash and GLM-5.3 join Table 2 when their AgentIssue-Bench runs and tests end.

## 3. Data and code

Every number is computed by `docs/selfheal_benchmark_tables_numbers.py`, which parses the two papers' tables from their arXiv pages and reads our run records, and its registry gives the source of each number.
