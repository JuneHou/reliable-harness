# Number registry, docs

Numbers of `docs/harness_repair_motivation_report.md` that appear in no other registry. The report is checked with

```
python3 ~/.claude/skills/number-check/scripts/check_numbers.py --registry motivation_pilot/NUMBERS.md --registry /data/wang/junh/githubs/AgentIssue-Bench/motivation_experiment/NUMBERS.md --registry docs/agentdefect_dataset_numbers.md --registry docs/NUMBERS.md --ignore '^7[6-9][0-9]{6},?$' --ignore '^[0-9]\.[0-9]$' docs/harness_repair_motivation_report.md
```

The two ignore patterns skip the eight digit AgentDefect case ids and the section numbers of the report.

| name | value | what it counts | source file | how it is computed | date read |
|---|---|---|---|---|---|
| review_multi_agent_entries | 29 | multi-agent or explicitly adjacent paper entries in the review | docs/Agent_Error_Mitigation_Review (1).html | section 1, "Inventory after revision" | 2026-10-23 |
| review_harness_entries | 21 | individual harness paper entries in the review | docs/Agent_Error_Mitigation_Review (1).html | section 1, "Inventory after revision"; updated 2026-10-30 to include DARC | 2026-10-30 |
| review_resource_audits | 15 | supplementary paper-specific resource audits in the review | docs/Agent_Error_Mitigation_Review (1).html | section 1, "Inventory after revision" | 2026-10-23 |
| review_cutoff_day | 19 | day of the literature cutoff, 19 October 2026 | docs/Agent_Error_Mitigation_Review (1).html | section 1, "Cutoff and sequence" | 2026-10-23 |
| review_row_car | 6 | row index of Causal Agent Replay in the review's section 8 table | docs/Agent_Error_Mitigation_Review (1).html | section 8 numbering | 2026-10-23 |
| review_row_dover | 15 | row index of DoVer in the review's section 8 table | docs/Agent_Error_Mitigation_Review (1).html | section 8 numbering | 2026-10-23 |
| review_row_gcjr | 22 | row index of MRFR / GCJR in the review's section 8 table | docs/Agent_Error_Mitigation_Review (1).html | section 8 numbering | 2026-10-23 |
| review_row_agenttether | 25 | row index of AgentTether in the review's section 8 table | docs/Agent_Error_Mitigation_Review (1).html | section 8 numbering | 2026-10-23 |
| review_row_sentry | 28 | row index of Sentry in the review's section 8 table | docs/Agent_Error_Mitigation_Review (1).html | section 8 numbering | 2026-10-23 |
| agentdefect_runs_all | 402 | runs recorded over the three AgentDefect experiments, 174 plus 36 plus 192 | motivation_pilot/artifacts/agentdefect_extension/*/runs.jsonl | sum of line counts | 2026-10-23 |
| agentdefect_cases_run | 6 | AgentDefect programs with runs in exp-2026-10-22 | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/experiment_manifest.json | CASE_ORDER | 2026-10-23 |
| agentdefect_offline_ready | 9 | offline ready cases of the 2026-10-20 pilot, six run plus three controls | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/report.md | section 1 case table | 2026-10-23 |
| e_comparisons_79343179 | 13 | comparisons of 79343179 in each environment of exp-2026-10-23-e | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-e/flips.jsonl | rows with case 79343179 | 2026-10-23 |
| agentissue_study_cases | 5 | AgentIssue-Bench cases in the removal study | /data/wang/junh/githubs/AgentIssue-Bench/motivation_experiment/exp-2026-10-21/report.md | section 1 | 2026-10-23 |
| repetitions_removable_margin_02 | 12 | runs a side at which P(abs delta < 0.2) first reaches 0.95 when both sides pass every run, 0.975 at 12 and 0.946 at 9 | motivation_pilot/src/motivation_pilot/verdict_stats.py | prob_delta_close(n, n, n, n, 0.2) over n | 2026-10-23 |
| repetitions_removable_margin_01 | 24 | runs a side at which P(abs delta < 0.1) first reaches 0.95 when both sides pass every run, 0.968 at 24 and 0.934 at 18 | motivation_pilot/src/motivation_pilot/verdict_stats.py | prob_delta_close(n, n, n, n, 0.1) over n | 2026-10-23 |
| ad_v_rows_total | 88 | total comparison rows in the AgentDefect reanalysis (exp-2026-10-23-v) | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/summary.json | rows field | 2026-10-29 |
| verdict_threshold | 0.95 | probability threshold used for required and removable verdicts; P(delta>0) at or above 0.95 for required, P(abs delta<delta) at or above 0.95 for removable | motivation_pilot/src/motivation_pilot/extension.py | LEVEL = 0.95 constant | 2026-10-29 |
| v_rows_both | 149 | comparison rows reanalysed over both datasets, 88 plus 61 | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/summary.json and /data/wang/junh/githubs/AgentIssue-Bench/motivation_experiment/exp-2026-10-23-v/summary.json | sum of rows | 2026-10-23 |
| ai_scored_runs | 315 | scored runs of the AgentIssue-Bench removal study, all with proxy_calls 0 | /data/wang/junh/githubs/AgentIssue-Bench/motivation_experiment/exp-2026-10-21/runs.jsonl | run_kind scored, proxy_calls counter | 2026-10-24 |
| ad_v_rows_full_execution | 72 | AgentDefect reanalysis rows whose every with side run executed the change | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | enactment.state observed and enacted equal to runs | 2026-10-25 |
| ad_v_rows_partial_execution | 1 | AgentDefect reanalysis rows with some but not all with side runs executing the change, 77178370 P_core two of nine | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | enactment.state observed and 0 < enacted < runs | 2026-10-25 |
| ad_v_rows_never_executable | 4 | AgentDefect reanalysis rows whose with side never executed the change, 76906469 B alone | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | enactment.state never_enacted | 2026-10-25 |
| ad_v_rows_not_observable | 11 | AgentDefect reanalysis rows whose change touches a module without a probe | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | enactment.state not_observable | 2026-10-25 |
| ai_scored_runs_flag_false | 12 | AgentIssue-Bench scored runs with reached_verdict or loaded_implementation_verified false, all evoninja_594, nine cited on without sides, none on a with side | /data/wang/junh/githubs/AgentIssue-Bench/motivation_experiment/exp-2026-10-21/runs.jsonl | run_kind scored and not (reached_verdict and loaded_implementation_verified), matched against comparisons run ids | 2026-10-25 |
| ai_594_devfix_files | 18 | files of the evoninja_594 developer fix | /data/wang/junh/githubs/AgentIssue-Bench/motivation_experiment/exp-2026-10-22/audit/boundary.json | len(developer_fix_files) of the public check | 2026-10-25 |
| ai_594_public_loaded | 3 | evoninja_594 developer fix files loaded by the authors' public check on the developer commit | /data/wang/junh/githubs/AgentIssue-Bench/motivation_experiment/exp-2026-10-22/audit/boundary.json | len(loaded) of the public check | 2026-10-25 |
| ai_515_public_loaded | 1 | evoninja_515 developer fix files loaded by the public check, of three | /data/wang/junh/githubs/AgentIssue-Bench/motivation_experiment/exp-2026-10-22/audit/boundary.json | len(loaded) of the public check | 2026-10-25 |
| ai_525_public_loaded | 3 | evoninja_525 developer fix files loaded by the public check, of four | /data/wang/junh/githubs/AgentIssue-Bench/motivation_experiment/exp-2026-10-22/audit/boundary.json | len(loaded) of the public check | 2026-10-25 |
| ad_v_cells_distinct | 264 | distinct (batch, comparison_id, side, cell) tuples of the AgentDefect reanalysis, one configuration and one input | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/cells.jsonl | set of the four fields | 2026-10-25 |
| ad_v_cells_deterministic | 256 | distinct cells whose k equals 0 or n, same outcome in every run | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/cells.jsonl | k in {0, n} over distinct cells | 2026-10-25 |
| ad_v_cells_mixed | 8 | distinct cells with 0 < k < n, six in 77178370 rows and two the published+R adventure cell of 78383658 | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/cells.jsonl | 0 < k < n over distinct cells | 2026-10-25 |
| hc_evolution_tasks | 50 | SWE-bench Verified evolution tasks HarnessCompass evolves on, per the review's extraction | docs/Agent_Error_Mitigation_Review (1).html | section 6 HarnessCompass, Learning, models and budget | 2026-10-25 |
| hc_heldout_tasks | 450 | unseen SWE-bench Verified tasks HarnessCompass is scored on, per the review's extraction | docs/Agent_Error_Mitigation_Review (1).html | section 6 HarnessCompass, Learning, models and budget | 2026-10-25 |
| component_table_retrieval_rows | 15 | rows of the dataset component table whose counted components include chunking, vector_store, a retrieval label or document_metadata | docs/agentdefect_component_table.csv | substring match on counted_components over the four label stems | 2026-10-26 |
| component_table_labels | 15 | distinct counted component labels in the dataset component table | docs/agentdefect_component_table.csv | split counted_components on commas, distinct nonempty | 2026-10-26 |
| pilot_scope_names | 14 | distinct scope names in COMPONENTS of the pilot code | motivation_pilot/src/motivation_pilot/extension.py | distinct values over COMPONENTS | 2026-10-26 |
| base_comparisons_79343179 | 13 | comparison rows for case 79343179 in exp-2026-10-22 | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/comparisons.jsonl | rows with case field 79343179 | 2026-10-27 |
| p_core_p_delta_pos | 0.92 | P(delta greater than zero) for the 77178370 P_core comparison in exp-2026-10-23-v, rounded to two decimal places | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | p_delta_positive of comparison_id 77178370:P_core pipe empty | 2026-10-27 |
| harness_fix_human_traces | 80 | human diagnosis traces used in HarnessFix verification, per the review extraction | docs/Agent_Error_Mitigation_Review (1).html | section 6 HarnessFix, Verification limits | 2026-10-27 |
| active_saddler_gain_low | 4.4 | lower of the two ActiveSaddler pass-rate gains in percentage points, per the review extraction | docs/Agent_Error_Mitigation_Review (1).html | section 6 ActiveSaddler, Reported result | 2026-10-27 |
| active_saddler_gain_high | 7.5 | higher of the two ActiveSaddler pass-rate gains in percentage points, per the review extraction | docs/Agent_Error_Mitigation_Review (1).html | section 6 ActiveSaddler, Reported result | 2026-10-27 |
| component_table_rows | 37 | data rows in docs/agentdefect_component_table.csv, 38 lines minus the header | docs/agentdefect_component_table.csv | wc -l minus 1 | 2026-10-27 |
| ai_bench_case_594 | 594 | AgentIssue-Bench case identifier for evoninja_594 used in the Q1 data point | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/audit/boundary.json | case field | 2026-10-27 |
| p_core_delta_mean | 0.30 | delta_mean for the 77178370 P_core comparison in exp-2026-10-23-v, rounded to two decimal places | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.delta_mean of comparison_id 77178370:P_core pipe empty | 2026-10-27 |
| confidence_level | 95 | confidence level percentage of the delta interval reported in the Q4 data table | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | fixed parameter of Jeffreys posterior interval | 2026-10-27 |
| p_core_delta_lo | 0.12 | absolute value of the lower bound of the 95 percent delta interval for the 77178370 P_core comparison, rounded to two decimal places | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | abs(contrast.delta_interval[0]) of comparison_id 77178370:P_core pipe empty | 2026-10-27 |
| p_core_delta_hi | 0.67 | upper bound of the 95 percent delta interval for the 77178370 P_core comparison, rounded to two decimal places | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.delta_interval[1] of comparison_id 77178370:P_core pipe empty | 2026-10-27 |
| p_core_enactment_rate | 0.22 | enactment rate pi for the 77178370 P_core comparison, rounded to two decimal places | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | enactment.rate of comparison_id 77178370:P_core pipe empty | 2026-10-27 |
| p_core_pn_ty | 0.462 | PN(T,Y) for 77178370 P_core comparison, Jeffreys posterior from k_with=6 and k_without=3 out of n=9 each | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | (k_with+0.5)/(n+1) minus (k_without+0.5)/(n+1) divided by (k_with+0.5)/(n+1); status completed_pass per arm | 2026-10-29 |
| p_core_k_with_s | 2 | runs in the P_core with-arm where the retrieval tool actually fires (kind=tool_call, stage=start) in the trace; out of 9 | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/traces | any event with kind tool_call and stage start in runs 77178370-P_core-*-p.jsonl | 2026-10-29 |
| p_core_k_without_s | 0 | runs in the original (without-arm) where the retrieval tool fires; out of 9 | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/traces | any event with kind tool_call and stage start in runs 77178370-original-*-p.jsonl | 2026-10-29 |
| p_core_pn_ts | 0.8 | ratio of Jeffreys posterior means for D (tool invocation) endpoint in 77178370 P_core arm; D is a different endpoint from Y; causal PN interpretation requires identification assumptions not verified here | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/traces | (k_with_D+0.5)/(n+1) minus (k_without_D+0.5)/(n+1) divided by (k_with_D+0.5)/(n+1); k_with_D=2, k_without_D=0, n=9 | 2026-10-30 |
| p_core_forward_suff | 1.0 | among with-arm runs where tool fired (D=1), share whose final check passed; both D=1 runs passed; D=1 is the tool invocation endpoint not the surrogate endpoint | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl and traces | runs where D=1 and status completed_pass divided by runs where D=1 in P_core arm | 2026-10-30 |
| p_core_direct_path | 0.57 | among with-arm runs where tool did not fire (D=0), share whose final check passed; 4 of 7 passed; shows D is insufficient as exact substitute for Y; does not establish Prentice condition failure | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl and traces | runs where D=0 and status completed_pass divided by non-invocation with-arm runs; 4 divided by 7 | 2026-10-30 |
| loader_pn_ts | 0.857 | ratio of Jeffreys posterior means where the boundary check equals Y by construction for 79343179 loader case; this is an identity control, not a validated surrogate for pipelines with later model calls | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | Jeffreys from k_with=3, k_without=0, n=3; boundary check and final check are the same variable | 2026-10-30 |
| loader_forward_suff | 1.0 | among with-arm runs in 79343179 loader case, share whose final check passed; trivially 1.0 because the boundary check equals Y by construction | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | all runs in 79343179-L1L2L3-*-p have status completed_pass; boundary check is Y | 2026-10-30 |
| modularrsi_tb20_base | 47.57 | base harness score on TaskBench 2.0 in ModularRSI's comparison table, per the review extraction | docs/Agent_Error_Mitigation_Review (1).html | section 6 ModularRSI, Reported result | 2026-10-27 |
| modularrsi_swe_ood_tb_acc | 49.44 | ModularRSI SWE-Related evolution out-of-domain accuracy on TerminalBench 2.0, DS-V4-Flash; also equals GLM-5.2 ModularRSI Pass3 in Table 2 | ModularRSI arXiv 2609.14857v2 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t1_noe_swe_acc | 73.40 | No Evolution accuracy on SWE-Bench-Verified, ModularRSI Table 1 | ModularRSI arXiv 2609.14857v2 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t1_noe_swe_p3 | 83.20 | No Evolution Pass@3 on SWE-Bench-Verified, ModularRSI Table 1 | ModularRSI arXiv 2609.14857v2 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t1_noe_swe_pass3 | 62.80 | No Evolution Pass3 on SWE-Bench-Verified, ModularRSI Table 1 | ModularRSI arXiv 2609.14857v2 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t1_tbr_swe_acc | 75.80 | TB-Related evolution out-of-domain accuracy on SWE-Bench-Verified, ModularRSI Table 1 | ModularRSI arXiv 2609.14857v2 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t1_tbr_swe_p3 | 84.60 | TB-Related evolution out-of-domain Pass@3 on SWE-Bench-Verified, ModularRSI Table 1 | ModularRSI arXiv 2609.14857v2 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t1_tbr_swe_pass3 | 66.20 | TB-Related evolution out-of-domain Pass3 on SWE-Bench-Verified, ModularRSI Table 1 | ModularRSI arXiv 2609.14857v2 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t1_swer_swe_acc | 76.40 | SWE-Related evolution in-domain accuracy on SWE-Bench-Verified, ModularRSI Table 1 | ModularRSI arXiv 2609.14857v2 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t1_swer_swe_p3 | 85.40 | SWE-Related evolution in-domain Pass@3 on SWE-Bench-Verified, ModularRSI Table 1 | ModularRSI arXiv 2609.14857v2 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t1_swer_swe_pass3 | 66.80 | SWE-Related evolution in-domain Pass3 on SWE-Bench-Verified, ModularRSI Table 1 | ModularRSI arXiv 2609.14857v2 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t1_noe_tb_p3 | 58.43 | No Evolution Pass@3 on TerminalBench 2.0, ModularRSI Table 1 | ModularRSI arXiv 2609.14857v2 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t1_noe_tb_pass3 | 30.34 | No Evolution Pass3 on TerminalBench 2.0; also appears in other ModularRSI cells with the same value | ModularRSI arXiv 2609.14857v2 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t1_tbr_tb_p3 | 65.17 | TB-Related evolution in-domain Pass@3 on TerminalBench 2.0, ModularRSI Table 1 | ModularRSI arXiv 2609.14857v2 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t1_tbr_tb_pass3 | 35.96 | TB-Related evolution in-domain Pass3 on TerminalBench 2.0, ModularRSI Table 1 | ModularRSI arXiv 2609.14857v2 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t1_swer_tb_p3 | 60.67 | SWE-Related evolution out-of-domain Pass@3 on TerminalBench 2.0, ModularRSI Table 1 | ModularRSI arXiv 2609.14857v2 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t2_glm_noe_acc | 59.55 | GLM-5.2 No-Evol Baseline accuracy on TerminalBench 2.0, ModularRSI Table 2 | ModularRSI arXiv 2609.14857v2 Table 2 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t2_glm_noe_p3 | 70.79 | GLM-5.2 No-Evol Baseline Pass@3 on TerminalBench 2.0, ModularRSI Table 2 | ModularRSI arXiv 2609.14857v2 Table 2 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t2_glm_noe_pass3 | 46.07 | GLM-5.2 No-Evol Baseline Pass3 on TerminalBench 2.0, ModularRSI Table 2 | ModularRSI arXiv 2609.14857v2 Table 2 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t2_glm_rsi_acc | 61.80 | GLM-5.2 ModularRSI accuracy on TerminalBench 2.0, ModularRSI Table 2 | ModularRSI arXiv 2609.14857v2 Table 2 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t2_glm_rsi_p3 | 74.16 | GLM-5.2 ModularRSI Pass@3 on TerminalBench 2.0, ModularRSI Table 2 | ModularRSI arXiv 2609.14857v2 Table 2 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t2_mm_noe_acc | 41.57 | MiniMax-2.5 No-Evol Baseline accuracy on TerminalBench 2.0, ModularRSI Table 2 | ModularRSI arXiv 2609.14857v2 Table 2 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t2_mm_noe_p3 | 56.18 | MiniMax-2.5 No-Evol Baseline Pass@3 on TerminalBench 2.0, ModularRSI Table 2 | ModularRSI arXiv 2609.14857v2 Table 2 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t2_mm_noe_pass3 | 24.72 | MiniMax-2.5 No-Evol Baseline Pass3 on TerminalBench 2.0, ModularRSI Table 2 | ModularRSI arXiv 2609.14857v2 Table 2 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t2_mm_rsi_acc | 44.94 | MiniMax-2.5 ModularRSI accuracy on TerminalBench 2.0, ModularRSI Table 2 | ModularRSI arXiv 2609.14857v2 Table 2 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_t2_mm_rsi_p3 | 57.30 | MiniMax-2.5 ModularRSI Pass@3 on TerminalBench 2.0, ModularRSI Table 2 | ModularRSI arXiv 2609.14857v2 Table 2 | provided by Jun 2026-10-28 | 2026-10-28 |
| modularrsi_tb20_score | 52.43 | ModularRSI score on TaskBench 2.0 in its comparison table, per the review extraction | docs/Agent_Error_Mitigation_Review (1).html | section 6 ModularRSI, Reported result | 2026-10-27 |
| rrsi_tb21_gain | 6.0 | RRSI gain over base on TaskBench 2.1, per the review extraction | docs/Agent_Error_Mitigation_Review (1).html | section 6 RRSI, Reported result | 2026-10-27 |
| rrsi_swe_ood_gain | 1.8 | RRSI gain over base on SWE-bench Verified OOD, per the review extraction | docs/Agent_Error_Mitigation_Review (1).html | section 6 RRSI, Reported result | 2026-10-27 |
| metaharness_vs_ace_gain | 7.7 | Meta-Harness gain over ACE on the classification task, per the review extraction | docs/Agent_Error_Mitigation_Review (1).html | section 6 Meta-Harness, Reported result | 2026-10-27 |
| selfheal_ad_fixes | 22 | SelfHeal fixes on AgentDefect 37 cases with Gemini3 Pro, per the review extraction | docs/Agent_Error_Mitigation_Review (1).html | section 6 SelfHeal, Reported result | 2026-10-27 |
| hc_t1_ahe_held | 54.0 | AHE Held-Out score on SWE-bench Verified in HarnessCompass Table 1, GPT5.4 non-thinking | HarnessCompass arXiv 2608.01918v1 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| hc_t1_ahe_total | 63.0 | AHE Total score on SWE-bench Verified in HarnessCompass Table 1 | HarnessCompass arXiv 2608.01918v1 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| hc_t1_hc_total | 66.0 | HarnessCompass Total score on SWE-bench Verified in HarnessCompass Table 1 | HarnessCompass arXiv 2608.01918v1 Table 1 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_zs_scic | 32.7 | Zero-shot accuracy on SciC in Meta-Harness Table 5 OOD evaluation | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_zs_finer | 56.0 | Zero-shot accuracy on FiNER in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_zs_amz5 | 52.7 | Zero-shot accuracy on Amz5 in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_zs_fpb | 90.0 | Zero-shot accuracy on FPB in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_zs_goemo | 42.0 | Zero-shot accuracy on GoEmo in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_zs_bank | 80.7 | Zero-shot accuracy on Bank77 in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_zs_news | 84.7 | Zero-shot accuracy on News in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_zs_scit | 89.3 | Zero-shot accuracy on SciT in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_zs_twhate | 75.3 | Zero-shot accuracy on TwHate in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_zs_avg | 67.0 | Zero-shot AvgAcc across 9 datasets in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs8_scic | 34.0 | Few-shot-8 accuracy on SciC in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs8_finer | 63.0 | Few-shot-8 accuracy on FiNER in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs8_amz5 | 54.0 | Few-shot-8 accuracy on Amz5 in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs8_goemo | 44.0 | Few-shot-8 accuracy on GoEmo in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs8_bank | 82.7 | Few-shot-8 accuracy on Bank77 in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs8_scit | 91.3 | Few-shot-8 accuracy on SciT in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs8_twhate | 76.7 | Few-shot-8 accuracy on TwHate in Meta-Harness Table 5; same value for fs32 and fs-all rows | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs8_avg | 68.9 | Few-shot-8 AvgAcc in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs8_ctx | 2.2 | Few-shot-8 context tokens (thousands) in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs32_scic | 38.7 | Few-shot-32 accuracy on SciC in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs32_finer | 62.0 | Few-shot-32 accuracy on FiNER in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs32_amz5 | 53.3 | Few-shot-32 accuracy on Amz5 in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs32_fpb | 90.7 | Few-shot-32 accuracy on FPB in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs32_goemo | 43.3 | Few-shot-32 accuracy on GoEmo in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs32_bank | 86.0 | Few-shot-32 accuracy on Bank77 in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs32_news | 85.3 | Few-shot-32 accuracy on News in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs32_avg | 69.6 | Few-shot-32 AvgAcc in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fs32_ctx | 5.2 | Few-shot-32 context tokens (thousands) in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fsall_scic | 35.3 | Few-shot-all accuracy on SciC in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fsall_finer | 61.0 | Few-shot-all accuracy on FiNER in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fsall_amz5 | 50.0 | Few-shot-all accuracy on Amz5 in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fsall_fpb | 93.3 | Few-shot-all accuracy on FPB in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fsall_goemo | 42.7 | Few-shot-all accuracy on GoEmo in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fsall_news | 84.0 | Few-shot-all accuracy on News in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fsall_avg | 68.2 | Few-shot-all AvgAcc in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_fsall_ctx | 7.4 | Few-shot-all context tokens (thousands) in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_ace_scic | 40.7 | ACE accuracy on SciC in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_ace_finer | 74.0 | ACE accuracy on FiNER in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_ace_amz5 | 48.0 | ACE accuracy on Amz5 in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_ace_fpb | 96.7 | ACE accuracy on FPB in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_ace_goemo | 44.0 | ACE accuracy on GoEmo in Meta-Harness Table 5; same value as Zero-shot GoEmo | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_ace_bank | 83.3 | ACE accuracy on Bank77 in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_ace_news | 86.0 | ACE accuracy on News in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_ace_scit | 90.7 | ACE accuracy on SciT in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_ace_twhate | 68.7 | ACE accuracy on TwHate in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_ace_avg | 70.2 | ACE AvgAcc across 9 datasets in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_ace_ctx | 11.7 | ACE context tokens (thousands) in Meta-Harness Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_mh_scic | 53.3 | Meta-Harness accuracy on SciC in Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_mh_finer | 67.0 | Meta-Harness accuracy on FiNER in Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_mh_amz5 | 60.0 | Meta-Harness accuracy on Amz5 in Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_mh_fpb | 94.0 | Meta-Harness accuracy on FPB in Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_mh_goemo | 46.0 | Meta-Harness accuracy on GoEmo in Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_mh_news | 86.7 | Meta-Harness accuracy on News in Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_mh_scit | 91.3 | Meta-Harness accuracy on SciT in Table 5; same value as Few-shot-8 SciT | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_mh_twhate | 77.3 | Meta-Harness accuracy on TwHate in Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_mh_avg | 73.1 | Meta-Harness AvgAcc across 9 OOD datasets in Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| mh_t5_mh_ctx | 7.3 | Meta-Harness context tokens (thousands) in Table 5 | Meta-Harness arXiv 2603.28052v1 Table 5 | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_h0_hle | 89.4 | H0 (no evolution) score on Harvey LAB Evolve in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_h0_hli | 86.9 | H0 score on Harvey LAB ID held-out in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_h0_jb | 36.0 | H0 score on JobBench in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_h0_gdp | 48.8 | H0 score on GDPval in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_h0_apex | 34.2 | H0 score on APEX-Agents in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_mh_hle | 93.0 | Meta-Harness score on Harvey LAB Evolve in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_mh_hli | 89.2 | Meta-Harness score on Harvey LAB ID held-out in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_mh_jb | 37.1 | Meta-Harness score on JobBench in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_mh_gdp | 49.1 | Meta-Harness score on GDPval in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_mh_apex | 35.7 | Meta-Harness score on APEX-Agents in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_ahe_hle | 90.7 | AHE score on Harvey LAB Evolve in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_ahe_hli | 88.7 | AHE score on Harvey LAB ID held-out in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_ahe_jb | 37.2 | AHE score on JobBench in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_ahe_gdp | 47.2 | AHE score on GDPval in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_ahe_apex | 33.1 | AHE score on APEX-Agents in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_tthe_hle | 91.1 | TTHE score on Harvey LAB Evolve in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_tthe_hli | 88.5 | TTHE score on Harvey LAB ID held-out in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_tthe_jb | 35.2 | TTHE score on JobBench in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_tthe_gdp | 47.0 | TTHE score on GDPval in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_tthe_apex | 31.7 | TTHE score on APEX-Agents in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_hx_hle | 91.8 | HarnessX score on Harvey LAB Evolve in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_hx_hli | 89.1 | HarnessX score on Harvey LAB ID held-out in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_hx_jb | 36.3 | HarnessX score on JobBench in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_hx_gdp | 48.5 | HarnessX score on GDPval in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_hx_apex | 34.3 | HarnessX score on APEX-Agents in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_rrsi_hle | 90.5 | RRSI score on Harvey LAB Evolve in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_rrsi_hli | 89.2 | RRSI score on Harvey LAB ID held-out in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_rrsi_jb | 40.7 | RRSI score on JobBench in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_rrsi_gdp | 52.3 | RRSI score on GDPval in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t1_rrsi_apex | 37.9 | RRSI score on APEX-Agents in RRSI Table 1 | RRSI arXiv 2609.24972v3 comparison table | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t3_opus_tb_h0 | 74.2 | H0 score on Terminal-Bench 2.1 Evolve, Claude Opus 4.8 policy, RRSI Table 3 | RRSI arXiv 2609.24972v3 Table 3 | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t3_opus_tb_rrsi | 80.2 | RRSI score on Terminal-Bench 2.1 Evolve, Claude Opus 4.8 policy, RRSI Table 3 | RRSI arXiv 2609.24972v3 Table 3 | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t3_opus_swe_h0 | 82.0 | H0 score on SWE-bench Verified OOD, Claude Opus 4.8 policy, RRSI Table 3 | RRSI arXiv 2609.24972v3 Table 3 | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t3_opus_swe_rrsi | 83.8 | RRSI score on SWE-bench Verified OOD, Claude Opus 4.8 policy, RRSI Table 3 | RRSI arXiv 2609.24972v3 Table 3 | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t3_gem_tb_h0 | 64.6 | H0 score on Terminal-Bench 2.1 Evolve, Gemini 3.5 Flash policy, RRSI Table 3 | RRSI arXiv 2609.24972v3 Table 3 | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t3_gem_tb_rrsi | 78.7 | RRSI score on Terminal-Bench 2.1 Evolve, Gemini 3.5 Flash policy, RRSI Table 3 | RRSI arXiv 2609.24972v3 Table 3 | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t3_gem_tb_delta | 14.1 | RRSI gain over H0 on Terminal-Bench 2.1 Evolve, Gemini 3.5 Flash policy, RRSI Table 3 | RRSI arXiv 2609.24972v3 Table 3 | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t3_gem_swe_h0 | 76.8 | H0 score on SWE-bench Verified OOD, Gemini 3.5 Flash policy, RRSI Table 3 | RRSI arXiv 2609.24972v3 Table 3 | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t3_gem_swe_rrsi | 79.0 | RRSI score on SWE-bench Verified OOD, Gemini 3.5 Flash policy, RRSI Table 3 | RRSI arXiv 2609.24972v3 Table 3 | provided by Jun 2026-10-28 | 2026-10-28 |
| rrsi_t3_gem_swe_delta | 2.2 | RRSI gain over H0 on SWE-bench Verified OOD, Gemini 3.5 Flash policy, RRSI Table 3 | RRSI arXiv 2609.24972v3 Table 3 | provided by Jun 2026-10-28 | 2026-10-28 |
| t1_pooled_success_z1 | 0.75 | P(Y=1 given Z_routing=1): 9 of 12 Z_routing=1 runs pass, 77178370 audit_E1 vs original, all input types and arms | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | count from confirmed 18-run table in docs/test1_surrogate_audit.md | 2026-10-31 |
| t1_mem_success_z1 | 1.00 | P(Y=1 given Z_memory=1): 3 of 3 Z_memory=1 runs pass, 76906469 AB vs original | motivation_pilot/artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | count from confirmed 6-run table in docs/test1_surrogate_audit.md | 2026-10-31 |
