# Number registry — motivation_pilot

| name | value | what it counts | source file | how it is computed | date read |
|---|---|---|---|---|---|

<!-- ext:start -->

| name | value | what it counts | source file | how it is computed | date read |
|---|---|---|---|---|---|
| ext_runs | 174 | runs recorded in runs.jsonl | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | line count | 2026-10-23 |
| ext_scheduled | 174 | scheduled executions | artifacts/agentdefect_extension/exp-2026-10-22/experiment_manifest.json | schedule length | 2026-10-23 |
| ext_model_enabled | 144 | scheduled episodes in model-enabled scopes | artifacts/agentdefect_extension/exp-2026-10-22/experiment_manifest.json | cases other than 79343179 | 2026-10-23 |
| ext_loader | 30 | scheduled loader episodes of 79343179 | artifacts/agentdefect_extension/exp-2026-10-22/experiment_manifest.json | case 79343179 | 2026-10-23 |
| ext_status_behavioral_failure | 121 | runs with status behavioral_failure | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | status count | 2026-10-23 |
| ext_status_completed_pass | 50 | runs with status completed_pass | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | status count | 2026-10-23 |
| ext_status_interface_runtime_failure | 3 | runs with status interface_runtime_failure | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | status count | 2026-10-23 |
| ext_programs | 6 | independent programs with runs | artifacts/agentdefect_extension/exp-2026-10-22/experiment_manifest.json | CASE_ORDER | 2026-10-23 |
| ext_controls | 3 | programs not run, failure not reproduced | artifacts/pilot_results.json | not_repaired | 2026-10-23 |
| ext_inputs | 12 | inputs over the six programs, a conversation counted once | artifacts/agentdefect_extension/exp-2026-10-22/experiment_manifest.json | case_inputs | 2026-10-23 |
| ext_configurations | 32 | configurations over the six programs | artifacts/agentdefect_extension/exp-2026-10-22/experiment_manifest.json | configurations | 2026-10-23 |
| ext_comparisons | 32 | with and without comparisons | artifacts/agentdefect_extension/exp-2026-10-22/experiment_manifest.json | comparisons | 2026-10-23 |
| ext_hist_groups | 12 | task groups of the historical 76906469 collection | cb39baa:repair_family_pilot/artifacts/donor_tables/runs.jsonl | distinct group_id | 2026-10-23 |
| ext_hist_repeats | 20 | repeats per group and arm in the historical collection | cb39baa:repair_family_pilot/artifacts/donor_tables/runs.jsonl | rows per group_id and repair_set, all equal | 2026-10-23 |
| ext_hist_empty_n | 240 | historical episodes of arm empty | cb39baa:repair_family_pilot/artifacts/donor_tables/runs.jsonl | rows with repair_set | 2026-10-23 |
| ext_hist_empty_ok | 0 | historical successes of arm empty | cb39baa:repair_family_pilot/artifacts/donor_tables/runs.jsonl | outcome success | 2026-10-23 |
| ext_hist_A_n | 240 | historical episodes of arm A | cb39baa:repair_family_pilot/artifacts/donor_tables/runs.jsonl | rows with repair_set | 2026-10-23 |
| ext_hist_A_ok | 0 | historical successes of arm A | cb39baa:repair_family_pilot/artifacts/donor_tables/runs.jsonl | outcome success | 2026-10-23 |
| ext_hist_B_n | 240 | historical episodes of arm B | cb39baa:repair_family_pilot/artifacts/donor_tables/runs.jsonl | rows with repair_set | 2026-10-23 |
| ext_hist_B_ok | 0 | historical successes of arm B | cb39baa:repair_family_pilot/artifacts/donor_tables/runs.jsonl | outcome success | 2026-10-23 |
| ext_hist_AB_n | 240 | historical episodes of arm AB | cb39baa:repair_family_pilot/artifacts/donor_tables/runs.jsonl | rows with repair_set | 2026-10-23 |
| ext_hist_AB_ok | 240 | historical successes of arm AB | cb39baa:repair_family_pilot/artifacts/donor_tables/runs.jsonl | outcome success | 2026-10-23 |
| ext_embedded_original | 0 | texts embedded by 78366661 original, repetition 1 | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | embed_documents counts in the trace | 2026-10-23 |
| ext_embedded_baseline | 0 | texts embedded by 78366661 baseline, repetition 1 | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | embed_documents counts in the trace | 2026-10-23 |
| ext_embedded_N | 0 | texts embedded by 78366661 N, repetition 1 | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | embed_documents counts in the trace | 2026-10-23 |
| ext_embedded_N_P1 | 362 | texts embedded by 78366661 N+P1, repetition 1 | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | embed_documents counts in the trace | 2026-10-23 |
| ext_embedded_N_P2 | 0 | texts embedded by 78366661 N+P2, repetition 1 | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | embed_documents counts in the trace | 2026-10-23 |
| ext_embedded_published | 367 | texts embedded by 78366661 published, repetition 1 | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | embed_documents counts in the trace | 2026-10-23 |
| ext_77099194_attempt_1_action_missing | 10 | missing for 77099194 attempt_1 action, repetition 1 | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | retrieval events in the trace and the check's missing list | 2026-10-23 |
| ext_77099194_attempt_1_adventure_missing | 10 | missing for 77099194 attempt_1 adventure, repetition 1 | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | retrieval events in the trace and the check's missing list | 2026-10-23 |
| ext_77099194_published_action_docs | 12 | docs for 77099194 published action, repetition 1 | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | retrieval events in the trace and the check's missing list | 2026-10-23 |
| ext_77099194_published_adventure_docs | 12 | docs for 77099194 published adventure, repetition 1 | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | retrieval events in the trace and the check's missing list | 2026-10-23 |
| ext_77099194_published_animation_docs | 12 | docs for 77099194 published animation, repetition 1 | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | retrieval events in the trace and the check's missing list | 2026-10-23 |
| ext_chat_requests | 127 | successful chat requests over all runs | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | sum of chat_requests | 2026-10-23 |
| ext_backend_attempts | 299 | model API network attempts in probed runs | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | sum of derived.backend_attempts | 2026-10-23 |
| ext_tokens_in | 68673 | chat input tokens over all runs | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | sum of tokens.prompt | 2026-10-23 |
| ext_tokens_out | 9326 | chat output tokens over all runs | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | sum of tokens.completion | 2026-10-23 |
| ext_embed_chars | 2250636 | characters sent to embedding calls in probed runs | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | sum of embedding_characters | 2026-10-23 |
| ext_cost | 0.07 | estimated dollars of recorded use | artifacts/agentdefect_extension/exp-2026-10-22/runs.jsonl | tokens times pilot_run.PRICE_IN and PRICE_OUT plus characters over four times 0.10 per million | 2026-10-23 |
| ext_r_runs | 36 | runs recorded in exp-2026-10-22-r | artifacts/agentdefect_extension/exp-2026-10-22-r/runs.jsonl | line count | 2026-10-23 |
| ext_r_scheduled | 36 | scheduled executions of exp-2026-10-22-r | artifacts/agentdefect_extension/exp-2026-10-22-r/experiment_manifest.json | schedule length | 2026-10-23 |
| ext_r_index | 12 | chunks indexed by 78383658 | artifacts/agentdefect_extension/exp-2026-10-22-r/experiment_manifest.json | CSVLoader and CharacterTextSplitter in memory | 2026-10-23 |
| ext_r_covered | 18 | R runs whose retrieval held every indexed chunk and whose final model request held every catalog title | artifacts/agentdefect_extension/exp-2026-10-22-r/decision.json | coverage rule | 2026-10-23 |
| ext_r_runs_r | 18 | runs of the two R configurations | artifacts/agentdefect_extension/exp-2026-10-22-r/decision.json | R runs with a trace | 2026-10-23 |
| ext_r_tokens_in | 52416 | chat input tokens in exp-2026-10-22-r | artifacts/agentdefect_extension/exp-2026-10-22-r/runs.jsonl | sum of tokens.prompt | 2026-10-23 |
| ext_r_tokens_out | 10550 | chat output tokens in exp-2026-10-22-r | artifacts/agentdefect_extension/exp-2026-10-22-r/runs.jsonl | sum of tokens.completion | 2026-10-23 |
| ext_e_runs | 192 | runs recorded in exp-2026-10-23-e | artifacts/agentdefect_extension/exp-2026-10-23-e/runs.jsonl | line count | 2026-10-23 |
| ext_e_scheduled | 192 | scheduled executions of exp-2026-10-23-e | artifacts/agentdefect_extension/exp-2026-10-23-e/experiment_manifest.json | schedule length | 2026-10-23 |
| ext_e_runs_e0 | 96 | E0 runs recorded in exp-2026-10-23-e | artifacts/agentdefect_extension/exp-2026-10-23-e/runs.jsonl | environment field | 2026-10-23 |
| ext_e_runs_e1 | 96 | E1 runs recorded in exp-2026-10-23-e | artifacts/agentdefect_extension/exp-2026-10-23-e/runs.jsonl | environment field | 2026-10-23 |
| ext_e_pandas_e1 | 2.2.3 | pandas version of the 79343179 E1 interpreter | /data/wang/junh/envs/harnessfix-pandas2 | pandas.__version__ | 2026-10-23 |
| ext_e_pandas_e0 | 3.0.6 | pandas version of the harnessfix interpreter | /data/wang/junh/envs/harnessfix | pandas.__version__ | 2026-10-23 |
| ext_e_catalog_rows_e1 | 96 | rows of the 78383658 E1 catalog control_96.csv | artifacts/agentdefect_extension/exp-2026-10-23-e/experiment_manifest.json | catalog_check.rows | 2026-10-23 |
| ext_e_catalog_rows_e0 | 12 | rows of the archive control.csv | artifacts/agentdefect_extension/exp-2026-10-23-e/experiment_manifest.json | rows minus added_rows | 2026-10-23 |
| ext_e_comparisons_observed | 22 | comparisons in cases whose E1 condition was observed | artifacts/agentdefect_extension/exp-2026-10-23-e/flips.jsonl | rows whose case is not environment_unresolved | 2026-10-23 |
| ext_e_flips | 2 | comparisons whose verdict differs between E0 and E1 | artifacts/agentdefect_extension/exp-2026-10-23-e/flips.jsonl | flipped true | 2026-10-23 |
| ext_e_comparisons | 26 | comparisons evaluated in each environment | artifacts/agentdefect_extension/exp-2026-10-23-e/flips.jsonl | line count | 2026-10-23 |
| ext_e_flips_unresolved | 2 | flipped comparisons in a case whose E1 endpoint returned an error | artifacts/agentdefect_extension/exp-2026-10-23-e/flips.jsonl | flipped and environment_unresolved | 2026-10-23 |
| ext_e_76906469_e1_http_status | 404 | HTTP status of the first E1 endpoint error of 76906469 | artifacts/agentdefect_extension/exp-2026-10-23-e/runs.jsonl | error_message | 2026-10-23 |
| ext_e_tokens_in | 283492 | chat input tokens in exp-2026-10-23-e | artifacts/agentdefect_extension/exp-2026-10-23-e/runs.jsonl | sum of tokens.prompt | 2026-10-23 |
| ext_e_tokens_out | 21295 | chat output tokens in exp-2026-10-23-e | artifacts/agentdefect_extension/exp-2026-10-23-e/runs.jsonl | sum of tokens.completion | 2026-10-23 |
| ext_e_embed_chars | 5208648 | characters sent to embedding calls in exp-2026-10-23-e | artifacts/agentdefect_extension/exp-2026-10-23-e/runs.jsonl | sum of embedding_characters | 2026-10-23 |
| ext_v_level | 0.95 | posterior probability level of the survival rules | artifacts/agentdefect_extension/exp-2026-10-23-v/summary.json | level | 2026-10-23 |
| ext_v_rows | 88 | comparison rows reanalysed in exp-2026-10-23-v | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | line count | 2026-10-23 |
| ext_v_rows_22 | 32 | reanalysed rows from exp-2026-10-22 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | batch field | 2026-10-23 |
| ext_v_rows_r | 4 | reanalysed rows from exp-2026-10-22-r | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | batch field | 2026-10-23 |
| ext_v_rows_e | 52 | reanalysed rows from exp-2026-10-23-e | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | batch field | 2026-10-23 |
| ext_v_not_admissible_rows | 8 | reanalysed rows with recorded verdict not_admissible | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | recorded_verdict | 2026-10-23 |
| ext_v_not_admissible_survives | 0 | not_admissible rows whose survival rule holds | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | survives true | 2026-10-23 |
| ext_v_not_admissible_fails | 0 | not_admissible rows whose survival rule fails | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | survives false | 2026-10-23 |
| ext_v_not_assessed_rows | 50 | reanalysed rows with recorded verdict not_assessed_parent_not_adequate | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | recorded_verdict | 2026-10-23 |
| ext_v_not_assessed_survives | 0 | not_assessed_parent_not_adequate rows whose survival rule holds | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | survives true | 2026-10-23 |
| ext_v_not_assessed_fails | 0 | not_assessed_parent_not_adequate rows whose survival rule fails | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | survives false | 2026-10-23 |
| ext_v_removable_rows | 8 | reanalysed rows with recorded verdict removable_in_context | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | recorded_verdict | 2026-10-23 |
| ext_v_removable_survives | 0 | removable_in_context rows whose survival rule holds | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | survives true | 2026-10-23 |
| ext_v_removable_fails | 8 | removable_in_context rows whose survival rule fails | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | survives false | 2026-10-23 |
| ext_v_required_rows | 22 | reanalysed rows with recorded verdict required_in_context | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | recorded_verdict | 2026-10-23 |
| ext_v_required_survives | 22 | required_in_context rows whose survival rule holds | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | survives true | 2026-10-23 |
| ext_v_required_fails | 0 | required_in_context rows whose survival rule fails | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | survives false | 2026-10-23 |
| ext_v_enacted_rows | 73 | rows whose with side enactment was observed | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | enactment.state observed | 2026-10-23 |
| ext_v_never | 4 | rows whose with side never enacted the change | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | enactment.state never_enacted | 2026-10-23 |
| ext_v_not_observable | 11 | rows whose change touches a module with no probe | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | enactment.state not_observable | 2026-10-23 |
| ext_v_partial0_k | 6 | with side passes of the partially enacted row | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | with.k | 2026-10-23 |
| ext_v_partial0_n | 9 | with side runs of the partially enacted row | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | with.n | 2026-10-23 |
| ext_v_partial0_e | 2 | enacted with side runs of the partially enacted row | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | enactment.enacted | 2026-10-23 |
| ext_v_partial0_r | 9 | with side runs of the partially enacted row | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | enactment.runs | 2026-10-23 |
| ext_v_required_three | 17 | required rows resting on three with side runs | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | required_in_context and with.n 3 | 2026-10-23 |
| ext_v_required_rows | 22 | required rows | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | recorded_verdict | 2026-10-23 |
| ext_v_fisher_three | 0.10 | Fisher p for three of three against zero of three | verdict_stats.fisher_p | computed | 2026-10-23 |
| ext_v_ppos_three | 0.996 | P(delta > 0) for three of three against zero of three | verdict_stats.contrast | computed | 2026-10-23 |
| ext_v_required_fisher | 17 | required rows with Fisher p at or above 0.05 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | fisher_p >= 0.05 | 2026-10-23 |
| ext_v_fisher_level | 0.05 | significance level of the Fisher count | report text | constant | 2026-10-23 |
| ext_v_removable_rows | 8 | removable rows | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | recorded_verdict | 2026-10-23 |
| ext_v_removable_survives | 0 | removable rows surviving at the margin | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | survives true | 2026-10-23 |
| ext_v_close_three | 0.72 | P(abs delta < 0.2) for three of three against three of three | verdict_stats.prob_delta_close | computed | 2026-10-23 |
| ext_v_close_nine | 0.95 | P(abs delta < 0.2) for nine of nine against nine of nine, 0.946 | verdict_stats.prob_delta_close | computed | 2026-10-23 |
| ext_v_margin | 0.2 | equivalence margin of the survival rule | artifacts/agentdefect_extension/exp-2026-10-23-v/summary.json | delta | 2026-10-23 |
| ext_v_margin_strict | 0.1 | the stricter margin reported beside the rule | verdict_stats.DELTAS | constant | 2026-10-23 |
| ext_v_required_g1_wk | 3 | with side passes, required_in_context rows with 3/3 against 0/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | with.k | 2026-10-23 |
| ext_v_required_g1_wn | 3 | with side runs, required_in_context rows with 3/3 against 0/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | with.n | 2026-10-23 |
| ext_v_required_g1_ok | 0 | without side passes, required_in_context rows with 3/3 against 0/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | without.k | 2026-10-23 |
| ext_v_required_g1_on | 3 | without side runs, required_in_context rows with 3/3 against 0/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | without.n | 2026-10-23 |
| ext_v_required_g1_rows | 17 | rows in the group, required_in_context rows with 3/3 against 0/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | count | 2026-10-23 |
| ext_v_required_g1_ppos | 1.00 | P(delta > 0), required_in_context rows with 3/3 against 0/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.p_delta_positive | 2026-10-23 |
| ext_v_required_g1_lo | 0.23 | lower end of the delta interval, required_in_context rows with 3/3 against 0/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.delta_interval[0] | 2026-10-23 |
| ext_v_required_g1_hi | 0.99 | upper end of the delta interval, required_in_context rows with 3/3 against 0/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.delta_interval[1] | 2026-10-23 |
| ext_v_required_g1_c1 | 0.01 | P(abs delta < 0.1), required_in_context rows with 3/3 against 0/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.p_delta_close 0.1 | 2026-10-23 |
| ext_v_required_g1_c2 | 0.02 | P(abs delta < 0.2), required_in_context rows with 3/3 against 0/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.p_delta_close 0.2 | 2026-10-23 |
| ext_v_required_g1_pn | 0.86 | PN at the posterior means, required_in_context rows with 3/3 against 0/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | pn | 2026-10-23 |
| ext_v_required_g1_fisher | 0.100 | Fisher exact two sided p, required_in_context rows with 3/3 against 0/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | fisher_p | 2026-10-23 |
| ext_v_required_g2_wk | 9 | with side passes, required_in_context rows with 9/9 against 0/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | with.k | 2026-10-23 |
| ext_v_required_g2_wn | 9 | with side runs, required_in_context rows with 9/9 against 0/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | with.n | 2026-10-23 |
| ext_v_required_g2_ok | 0 | without side passes, required_in_context rows with 9/9 against 0/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | without.k | 2026-10-23 |
| ext_v_required_g2_on | 9 | without side runs, required_in_context rows with 9/9 against 0/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | without.n | 2026-10-23 |
| ext_v_required_g2_rows | 5 | rows in the group, required_in_context rows with 9/9 against 0/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | count | 2026-10-23 |
| ext_v_required_g2_ppos | 1.00 | P(delta > 0), required_in_context rows with 9/9 against 0/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.p_delta_positive | 2026-10-23 |
| ext_v_required_g2_lo | 0.66 | lower end of the delta interval, required_in_context rows with 9/9 against 0/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.delta_interval[0] | 2026-10-23 |
| ext_v_required_g2_hi | 1.00 | upper end of the delta interval, required_in_context rows with 9/9 against 0/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.delta_interval[1] | 2026-10-23 |
| ext_v_required_g2_c1 | 0.00 | P(abs delta < 0.1), required_in_context rows with 9/9 against 0/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.p_delta_close 0.1 | 2026-10-23 |
| ext_v_required_g2_c2 | 0.00 | P(abs delta < 0.2), required_in_context rows with 9/9 against 0/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.p_delta_close 0.2 | 2026-10-23 |
| ext_v_required_g2_pn | 0.95 | PN at the posterior means, required_in_context rows with 9/9 against 0/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | pn | 2026-10-23 |
| ext_v_required_g2_fisher | 0.000 | Fisher exact two sided p, required_in_context rows with 9/9 against 0/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | fisher_p | 2026-10-23 |
| ext_v_removable_g1_wk | 3 | with side passes, removable_in_context rows with 3/3 against 3/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | with.k | 2026-10-23 |
| ext_v_removable_g1_wn | 3 | with side runs, removable_in_context rows with 3/3 against 3/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | with.n | 2026-10-23 |
| ext_v_removable_g1_ok | 3 | without side passes, removable_in_context rows with 3/3 against 3/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | without.k | 2026-10-23 |
| ext_v_removable_g1_on | 3 | without side runs, removable_in_context rows with 3/3 against 3/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | without.n | 2026-10-23 |
| ext_v_removable_g1_rows | 3 | rows in the group, removable_in_context rows with 3/3 against 3/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | count | 2026-10-23 |
| ext_v_removable_g1_ppos | 0.50 | P(delta > 0), removable_in_context rows with 3/3 against 3/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.p_delta_positive | 2026-10-23 |
| ext_v_removable_g1_lo | -0.46 | lower end of the delta interval, removable_in_context rows with 3/3 against 3/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.delta_interval[0] | 2026-10-23 |
| ext_v_removable_g1_hi | 0.46 | upper end of the delta interval, removable_in_context rows with 3/3 against 3/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.delta_interval[1] | 2026-10-23 |
| ext_v_removable_g1_c1 | 0.50 | P(abs delta < 0.1), removable_in_context rows with 3/3 against 3/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.p_delta_close 0.1 | 2026-10-23 |
| ext_v_removable_g1_c2 | 0.72 | P(abs delta < 0.2), removable_in_context rows with 3/3 against 3/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.p_delta_close 0.2 | 2026-10-23 |
| ext_v_removable_g1_pn | 0.00 | PN at the posterior means, removable_in_context rows with 3/3 against 3/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | pn | 2026-10-23 |
| ext_v_removable_g1_fisher | 1.000 | Fisher exact two sided p, removable_in_context rows with 3/3 against 3/3, enacted 3/3 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | fisher_p | 2026-10-23 |
| ext_v_removable_g2_wk | 3 | with side passes, removable_in_context rows with 3/3 against 3/3, enacted not observable | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | with.k | 2026-10-23 |
| ext_v_removable_g2_wn | 3 | with side runs, removable_in_context rows with 3/3 against 3/3, enacted not observable | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | with.n | 2026-10-23 |
| ext_v_removable_g2_ok | 3 | without side passes, removable_in_context rows with 3/3 against 3/3, enacted not observable | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | without.k | 2026-10-23 |
| ext_v_removable_g2_on | 3 | without side runs, removable_in_context rows with 3/3 against 3/3, enacted not observable | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | without.n | 2026-10-23 |
| ext_v_removable_g2_rows | 3 | rows in the group, removable_in_context rows with 3/3 against 3/3, enacted not observable | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | count | 2026-10-23 |
| ext_v_removable_g2_ppos | 0.50 | P(delta > 0), removable_in_context rows with 3/3 against 3/3, enacted not observable | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.p_delta_positive | 2026-10-23 |
| ext_v_removable_g2_lo | -0.46 | lower end of the delta interval, removable_in_context rows with 3/3 against 3/3, enacted not observable | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.delta_interval[0] | 2026-10-23 |
| ext_v_removable_g2_hi | 0.46 | upper end of the delta interval, removable_in_context rows with 3/3 against 3/3, enacted not observable | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.delta_interval[1] | 2026-10-23 |
| ext_v_removable_g2_c1 | 0.50 | P(abs delta < 0.1), removable_in_context rows with 3/3 against 3/3, enacted not observable | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.p_delta_close 0.1 | 2026-10-23 |
| ext_v_removable_g2_c2 | 0.72 | P(abs delta < 0.2), removable_in_context rows with 3/3 against 3/3, enacted not observable | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.p_delta_close 0.2 | 2026-10-23 |
| ext_v_removable_g2_pn | 0.00 | PN at the posterior means, removable_in_context rows with 3/3 against 3/3, enacted not observable | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | pn | 2026-10-23 |
| ext_v_removable_g2_fisher | 1.000 | Fisher exact two sided p, removable_in_context rows with 3/3 against 3/3, enacted not observable | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | fisher_p | 2026-10-23 |
| ext_v_removable_g3_wk | 9 | with side passes, removable_in_context rows with 9/9 against 9/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | with.k | 2026-10-23 |
| ext_v_removable_g3_wn | 9 | with side runs, removable_in_context rows with 9/9 against 9/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | with.n | 2026-10-23 |
| ext_v_removable_g3_ok | 9 | without side passes, removable_in_context rows with 9/9 against 9/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | without.k | 2026-10-23 |
| ext_v_removable_g3_on | 9 | without side runs, removable_in_context rows with 9/9 against 9/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | without.n | 2026-10-23 |
| ext_v_removable_g3_rows | 2 | rows in the group, removable_in_context rows with 9/9 against 9/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | count | 2026-10-23 |
| ext_v_removable_g3_ppos | 0.50 | P(delta > 0), removable_in_context rows with 9/9 against 9/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.p_delta_positive | 2026-10-23 |
| ext_v_removable_g3_lo | -0.21 | lower end of the delta interval, removable_in_context rows with 9/9 against 9/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.delta_interval[0] | 2026-10-23 |
| ext_v_removable_g3_hi | 0.21 | upper end of the delta interval, removable_in_context rows with 9/9 against 9/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.delta_interval[1] | 2026-10-23 |
| ext_v_removable_g3_c1 | 0.79 | P(abs delta < 0.1), removable_in_context rows with 9/9 against 9/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.p_delta_close 0.1 | 2026-10-23 |
| ext_v_removable_g3_c2 | 0.95 | P(abs delta < 0.2), removable_in_context rows with 9/9 against 9/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | contrast.p_delta_close 0.2 | 2026-10-23 |
| ext_v_removable_g3_pn | 0.00 | PN at the posterior means, removable_in_context rows with 9/9 against 9/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | pn | 2026-10-23 |
| ext_v_removable_g3_fisher | 1.000 | Fisher exact two sided p, removable_in_context rows with 9/9 against 9/9, enacted 9/9 | artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl | fisher_p | 2026-10-23 |

<!-- ext:end -->
