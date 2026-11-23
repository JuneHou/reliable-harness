# Number registry, SelfHeal against the published benchmarks

Rows written by `docs/selfheal_benchmark_tables_numbers.py`. Checked with

```
python3 ~/.claude/skills/number-check/scripts/check_numbers.py --registry docs/selfheal_benchmark_tables_numbers.md --ignore '^[0-9]\.[0-9](\.[0-9])?$' --ignore '^(2604\.17699|2505\.20749)$' docs/selfheal_benchmark_tables.md
```

| name | value | what it counts | source file | how it is computed | date read |
|---|---|---|---|---|---|
| sh_t2_SWEA_G52_repair | 0.3784 | SelfHeal paper Table 2, SWE-A with G5.2, column repair | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SWEA_G52_line | 0.4865 | SelfHeal paper Table 2, SWE-A with G5.2, column line | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SWEA_G52_fn | 0.7297 | SelfHeal paper Table 2, SWE-A with G5.2, column fn | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SWEA_G52_comp | 0.8108 | SelfHeal paper Table 2, SWE-A with G5.2, column comp | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SWEA_G52_attempts | 3.78 | SelfHeal paper Table 2, SWE-A with G5.2, column attempts | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_Zeroshot_G52_repair | 0.3243 | SelfHeal paper Table 2, Zero-shot with G5.2, column repair | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_Zeroshot_G52_line | 0.4865 | SelfHeal paper Table 2, Zero-shot with G5.2, column line | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_Zeroshot_G52_fn | 0.5946 | SelfHeal paper Table 2, Zero-shot with G5.2, column fn | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_Zeroshot_G52_comp | 0.6486 | SelfHeal paper Table 2, Zero-shot with G5.2, column comp | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_Zeroshot_G52_attempts | 1.00 | SelfHeal paper Table 2, Zero-shot with G5.2, column attempts | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_Zeroshot_G3P_repair | 0.3514 | SelfHeal paper Table 2, Zero-shot with G3P, column repair | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_Zeroshot_G3P_line | 0.5135 | SelfHeal paper Table 2, Zero-shot with G3P, column line | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_Zeroshot_G3P_fn | 0.7838 | SelfHeal paper Table 2, Zero-shot with G3P, column fn | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_Zeroshot_G3P_comp | 0.8108 | SelfHeal paper Table 2, Zero-shot with G3P, column comp | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_Zeroshot_G3P_attempts | 1.00 | SelfHeal paper Table 2, Zero-shot with G3P, column attempts | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_Zeroshot_CS4_repair | 0.4054 | SelfHeal paper Table 2, Zero-shot with CS4, column repair | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_Zeroshot_CS4_line | 0.5946 | SelfHeal paper Table 2, Zero-shot with CS4, column line | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_Zeroshot_CS4_fn | 0.7838 | SelfHeal paper Table 2, Zero-shot with CS4, column fn | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_Zeroshot_CS4_comp | 0.8649 | SelfHeal paper Table 2, Zero-shot with CS4, column comp | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_Zeroshot_CS4_attempts | 1.00 | SelfHeal paper Table 2, Zero-shot with CS4, column attempts | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_NFR_G3P_repair | 0.4054 | SelfHeal paper Table 2, NFR with G3P, column repair | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_NFR_G3P_line | 0.5676 | SelfHeal paper Table 2, NFR with G3P, column line | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_NFR_G3P_fn | 0.7568 | SelfHeal paper Table 2, NFR with G3P, column fn | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_NFR_G3P_comp | 0.8919 | SelfHeal paper Table 2, NFR with G3P, column comp | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_NFR_G3P_attempts | 1.30 | SelfHeal paper Table 2, NFR with G3P, column attempts | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_NWS_G3P_repair | 0.4595 | SelfHeal paper Table 2, NWS with G3P, column repair | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_NWS_G3P_line | 0.5135 | SelfHeal paper Table 2, NWS with G3P, column line | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_NWS_G3P_fn | 0.8378 | SelfHeal paper Table 2, NWS with G3P, column fn | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_NWS_G3P_comp | 0.8649 | SelfHeal paper Table 2, NWS with G3P, column comp | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_NWS_G3P_attempts | 1.24 | SelfHeal paper Table 2, NWS with G3P, column attempts | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_NCA_G3P_repair | 0.5135 | SelfHeal paper Table 2, NCA with G3P, column repair | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_NCA_G3P_line | 0.7297 | SelfHeal paper Table 2, NCA with G3P, column line | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_NCA_G3P_fn | 0.8378 | SelfHeal paper Table 2, NCA with G3P, column fn | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_NCA_G3P_comp | 0.9189 | SelfHeal paper Table 2, NCA with G3P, column comp | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_NCA_G3P_attempts | 1.32 | SelfHeal paper Table 2, NCA with G3P, column attempts | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SelfHeal_G52_repair | 0.5405 | SelfHeal paper Table 2, SelfHeal with G5.2, column repair | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SelfHeal_G52_line | 0.6486 | SelfHeal paper Table 2, SelfHeal with G5.2, column line | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SelfHeal_G52_fn | 0.7838 | SelfHeal paper Table 2, SelfHeal with G5.2, column fn | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SelfHeal_G52_comp | 0.8919 | SelfHeal paper Table 2, SelfHeal with G5.2, column comp | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SelfHeal_G52_attempts | 1.35 | SelfHeal paper Table 2, SelfHeal with G5.2, column attempts | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SelfHeal_G3P_repair | 0.5946 | SelfHeal paper Table 2, SelfHeal with G3P, column repair | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SelfHeal_G3P_line | 0.7297 | SelfHeal paper Table 2, SelfHeal with G3P, column line | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SelfHeal_G3P_fn | 0.8378 | SelfHeal paper Table 2, SelfHeal with G3P, column fn | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SelfHeal_G3P_comp | 0.9189 | SelfHeal paper Table 2, SelfHeal with G3P, column comp | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SelfHeal_G3P_attempts | 1.32 | SelfHeal paper Table 2, SelfHeal with G3P, column attempts | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SelfHeal_CS4_repair | 0.5676 | SelfHeal paper Table 2, SelfHeal with CS4, column repair | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SelfHeal_CS4_line | 0.7297 | SelfHeal paper Table 2, SelfHeal with CS4, column line | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SelfHeal_CS4_fn | 0.7838 | SelfHeal paper Table 2, SelfHeal with CS4, column fn | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SelfHeal_CS4_comp | 0.8919 | SelfHeal paper Table 2, SelfHeal with CS4, column comp | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_t2_SelfHeal_CS4_attempts | 1.05 | SelfHeal paper Table 2, SelfHeal with CS4, column attempts | SelfHeal paper arXiv 2604.17699 v1, Table 2 | copied | 2026-11-16 |
| sh_cases | 37 | AgentDefect cases in the SelfHeal paper's evaluation | SelfHeal paper §4.3.1 | 'correctly fixing 22 out of 37' | 2026-11-16 |
| sheet_g52_37_resolved | 20 | cases marked Resolved, results-agent-gpt, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gpt | sum of the Resolved column | 2026-11-16 |
| sheet_g52_37_rate | 0.5405 | share of cases marked Resolved, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gpt | Resolved sum / cases | 2026-11-16 |
| sheet_g52_37_line | 0.6486 | share of cases localized at line level, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gpt | line sum / cases | 2026-11-16 |
| sheet_g52_37_function | 0.7838 | share of cases localized at function level, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gpt | function sum / cases | 2026-11-16 |
| sheet_g52_37_component | 0.8919 | share of cases localized at component level, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gpt | component sum / cases | 2026-11-16 |
| sheet_g52_37_attempts | 1.35 | mean attempts per case, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gpt | mean of the Attempts column | 2026-11-16 |
| sheet_g52_37_seconds | 41.8 | mean time per case in seconds, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gpt | mean of the Time column | 2026-11-16 |
| sheet_g52_36_resolved | 20 | cases marked Resolved, results-agent-gpt, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gpt | sum of the Resolved column | 2026-11-16 |
| sheet_g52_36_rate | 0.5556 | share of cases marked Resolved, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gpt | Resolved sum / cases | 2026-11-16 |
| sheet_g52_36_line | 0.6667 | share of cases localized at line level, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gpt | line sum / cases | 2026-11-16 |
| sheet_g52_36_function | 0.8056 | share of cases localized at function level, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gpt | function sum / cases | 2026-11-16 |
| sheet_g52_36_component | 0.9167 | share of cases localized at component level, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gpt | component sum / cases | 2026-11-16 |
| sheet_g52_36_attempts | 1.36 | mean attempts per case, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gpt | mean of the Attempts column | 2026-11-16 |
| sheet_g52_36_seconds | 42.0 | mean time per case in seconds, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gpt | mean of the Time column | 2026-11-16 |
| sheet_g3p_37_resolved | 22 | cases marked Resolved, results-agent-gemini, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gemini | sum of the Resolved column | 2026-11-16 |
| sheet_g3p_37_rate | 0.5946 | share of cases marked Resolved, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gemini | Resolved sum / cases | 2026-11-16 |
| sheet_g3p_37_line | 0.7297 | share of cases localized at line level, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gemini | line sum / cases | 2026-11-16 |
| sheet_g3p_37_function | 0.8378 | share of cases localized at function level, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gemini | function sum / cases | 2026-11-16 |
| sheet_g3p_37_component | 0.9189 | share of cases localized at component level, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gemini | component sum / cases | 2026-11-16 |
| sheet_g3p_37_attempts | 1.32 | mean attempts per case, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gemini | mean of the Attempts column | 2026-11-16 |
| sheet_g3p_37_seconds | 322.7 | mean time per case in seconds, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gemini | mean of the Time column | 2026-11-16 |
| sheet_g3p_36_resolved | 22 | cases marked Resolved, results-agent-gemini, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gemini | sum of the Resolved column | 2026-11-16 |
| sheet_g3p_36_rate | 0.6111 | share of cases marked Resolved, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gemini | Resolved sum / cases | 2026-11-16 |
| sheet_g3p_36_line | 0.7500 | share of cases localized at line level, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gemini | line sum / cases | 2026-11-16 |
| sheet_g3p_36_function | 0.8611 | share of cases localized at function level, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gemini | function sum / cases | 2026-11-16 |
| sheet_g3p_36_component | 0.9444 | share of cases localized at component level, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gemini | component sum / cases | 2026-11-16 |
| sheet_g3p_36_attempts | 1.33 | mean attempts per case, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gemini | mean of the Attempts column | 2026-11-16 |
| sheet_g3p_36_seconds | 318.4 | mean time per case in seconds, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-gemini | mean of the Time column | 2026-11-16 |
| sheet_cs4_37_resolved | 21 | cases marked Resolved, results-agent-claude, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-claude | sum of the Resolved column | 2026-11-16 |
| sheet_cs4_37_rate | 0.5676 | share of cases marked Resolved, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-claude | Resolved sum / cases | 2026-11-16 |
| sheet_cs4_37_line | 0.7838 | share of cases localized at line level, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-claude | line sum / cases | 2026-11-16 |
| sheet_cs4_37_function | 0.7838 | share of cases localized at function level, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-claude | function sum / cases | 2026-11-16 |
| sheet_cs4_37_component | 0.8919 | share of cases localized at component level, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-claude | component sum / cases | 2026-11-16 |
| sheet_cs4_37_attempts | 1.05 | mean attempts per case, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-claude | mean of the Attempts column | 2026-11-16 |
| sheet_cs4_37_seconds | 43.4 | mean time per case in seconds, 37 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-claude | mean of the Time column | 2026-11-16 |
| sheet_cs4_36_resolved | 21 | cases marked Resolved, results-agent-claude, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-claude | sum of the Resolved column | 2026-11-16 |
| sheet_cs4_36_rate | 0.5833 | share of cases marked Resolved, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-claude | Resolved sum / cases | 2026-11-16 |
| sheet_cs4_36_line | 0.8056 | share of cases localized at line level, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-claude | line sum / cases | 2026-11-16 |
| sheet_cs4_36_function | 0.8056 | share of cases localized at function level, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-claude | function sum / cases | 2026-11-16 |
| sheet_cs4_36_component | 0.9167 | share of cases localized at component level, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-claude | component sum / cases | 2026-11-16 |
| sheet_cs4_36_attempts | 1.06 | mean attempts per case, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-claude | mean of the Attempts column | 2026-11-16 |
| sheet_cs4_36_seconds | 43.6 | mean time per case in seconds, 36 cases | /data/wang/junh/githubs/SelfHeal/Detailed Result.xlsx, sheet results-agent-claude | mean of the Time column | 2026-11-16 |
| ad_gpt_succ_mean | 0.3000 | gpt-oss-120b, share of the 36 cases where the critic accepted and the test passed, mean over five runs | AgentDefect/SelfHeal/test_scores.csv | per run share, mean | 2026-11-16 |
| ad_gpt_succ_2s | 0.1069 | gpt-oss-120b, two standard deviations of that share over the five runs | AgentDefect/SelfHeal/test_scores.csv | 2 x sample sd over runs | 2026-11-16 |
| ad_gpt_test_mean | 0.3000 | gpt-oss-120b, share of the 36 cases whose returned code passed the test, mean over five runs | AgentDefect/SelfHeal/test_scores.csv | per run share, mean | 2026-11-16 |
| ad_gpt_test_2s | 0.1069 | gpt-oss-120b, two standard deviations of that share over the five runs | AgentDefect/SelfHeal/test_scores.csv | 2 x sample sd over runs | 2026-11-16 |
| ad_gpt_accepted | 138 | gpt-oss-120b, runs the critic accepted, of 180 | AgentDefect/SelfHeal/test_scores.csv | final_status ACCEPTED | 2026-11-16 |
| ad_gpt_attempts | 1.65 | gpt-oss-120b, mean attempts per run | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results | mean of Final Attempt | 2026-11-16 |
| ad_gpt_attempt_runs | 180 | gpt-oss-120b, runs with a result file | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results | count | 2026-11-16 |
| ad_gpt_seconds | 84.9 | gpt-oss-120b, mean SelfHeal time per run in seconds | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/run_record.json | mean of summed attempt seconds | 2026-11-16 |
| ad_gpt_seconds_runs | 180 | gpt-oss-120b, runs with a time record | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/run_record.json | count | 2026-11-16 |
| ad_deepseek_succ_mean | 0.4722 | DeepSeek-V4.1-Flash, share of the 36 cases where the critic accepted and the test passed, mean over five runs | AgentDefect/SelfHeal/test_scores.csv | per run share, mean | 2026-11-16 |
| ad_deepseek_succ_2s | 0.1179 | DeepSeek-V4.1-Flash, two standard deviations of that share over the five runs | AgentDefect/SelfHeal/test_scores.csv | 2 x sample sd over runs | 2026-11-16 |
| ad_deepseek_test_mean | 0.4722 | DeepSeek-V4.1-Flash, share of the 36 cases whose returned code passed the test, mean over five runs | AgentDefect/SelfHeal/test_scores.csv | per run share, mean | 2026-11-16 |
| ad_deepseek_test_2s | 0.1179 | DeepSeek-V4.1-Flash, two standard deviations of that share over the five runs | AgentDefect/SelfHeal/test_scores.csv | 2 x sample sd over runs | 2026-11-16 |
| ad_deepseek_accepted | 180 | DeepSeek-V4.1-Flash, runs the critic accepted, of 180 | AgentDefect/SelfHeal/test_scores.csv | final_status ACCEPTED | 2026-11-16 |
| ad_deepseek_attempts | 1.05 | DeepSeek-V4.1-Flash, mean attempts per run | AgentDefect/SelfHeal/DeepSeek-V4.1-Flash/<case>/rerun_<k>/Fix-Agent/results | mean of Final Attempt | 2026-11-16 |
| ad_deepseek_attempt_runs | 180 | DeepSeek-V4.1-Flash, runs with a result file | AgentDefect/SelfHeal/DeepSeek-V4.1-Flash/<case>/rerun_<k>/Fix-Agent/results | count | 2026-11-16 |
| ad_deepseek_seconds | 331.5 | DeepSeek-V4.1-Flash, mean SelfHeal time per run in seconds | AgentDefect/SelfHeal/DeepSeek-V4.1-Flash/<case>/rerun_<k>/run_record.json | mean of summed attempt seconds | 2026-11-16 |
| ad_deepseek_seconds_runs | 180 | DeepSeek-V4.1-Flash, runs with a time record | AgentDefect/SelfHeal/DeepSeek-V4.1-Flash/<case>/rerun_<k>/run_record.json | count | 2026-11-16 |
| ad_glm_succ_mean | 0.4722 | GLM-5.3, share of the 36 cases where the critic accepted and the test passed, mean over five runs | AgentDefect/SelfHeal/test_scores.csv | per run share, mean | 2026-11-16 |
| ad_glm_succ_2s | 0.0680 | GLM-5.3, two standard deviations of that share over the five runs | AgentDefect/SelfHeal/test_scores.csv | 2 x sample sd over runs | 2026-11-16 |
| ad_glm_test_mean | 0.4722 | GLM-5.3, share of the 36 cases whose returned code passed the test, mean over five runs | AgentDefect/SelfHeal/test_scores.csv | per run share, mean | 2026-11-16 |
| ad_glm_test_2s | 0.0680 | GLM-5.3, two standard deviations of that share over the five runs | AgentDefect/SelfHeal/test_scores.csv | 2 x sample sd over runs | 2026-11-16 |
| ad_glm_accepted | 180 | GLM-5.3, runs the critic accepted, of 180 | AgentDefect/SelfHeal/test_scores.csv | final_status ACCEPTED | 2026-11-16 |
| ad_glm_attempts | 1.06 | GLM-5.3, mean attempts per run | AgentDefect/SelfHeal/GLM-5.3/<case>/rerun_<k>/Fix-Agent/results | mean of Final Attempt | 2026-11-16 |
| ad_glm_attempt_runs | 180 | GLM-5.3, runs with a result file | AgentDefect/SelfHeal/GLM-5.3/<case>/rerun_<k>/Fix-Agent/results | count | 2026-11-16 |
| ad_glm_seconds | 812.8 | GLM-5.3, mean SelfHeal time per run in seconds | AgentDefect/SelfHeal/GLM-5.3/<case>/rerun_<k>/run_record.json | mean of summed attempt seconds | 2026-11-16 |
| ad_glm_seconds_runs | 180 | GLM-5.3, runs with a time record | AgentDefect/SelfHeal/GLM-5.3/<case>/rerun_<k>/run_record.json | count | 2026-11-16 |
| ad37_gpt_succ_mean | 0.2919 | gpt-oss-120b, share of the 37 cases where the critic accepted and the test passed, mean over five runs | AgentDefect/SelfHeal/test_scores.csv | per run share of 37, mean | 2026-11-16 |
| ad37_gpt_succ_2s | 0.1040 | gpt-oss-120b, two standard deviations of that share over five runs | AgentDefect/SelfHeal/test_scores.csv | 2 x sample sd | 2026-11-16 |
| ad37_gpt_attempts | 1.69 | gpt-oss-120b, mean attempts per run over the 37 cases | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results | mean of Final Attempt | 2026-11-16 |
| ad37_gpt_attempt_runs | 185 | gpt-oss-120b, runs with a result file over the 37 cases | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results | count | 2026-11-16 |
| ad37_deepseek_succ_mean | 0.4595 | DeepSeek-V4.1-Flash, share of the 37 cases where the critic accepted and the test passed, mean over five runs | AgentDefect/SelfHeal/test_scores.csv | per run share of 37, mean | 2026-11-16 |
| ad37_deepseek_succ_2s | 0.1147 | DeepSeek-V4.1-Flash, two standard deviations of that share over five runs | AgentDefect/SelfHeal/test_scores.csv | 2 x sample sd | 2026-11-16 |
| ad37_deepseek_attempts | 1.05 | DeepSeek-V4.1-Flash, mean attempts per run over the 37 cases | AgentDefect/SelfHeal/DeepSeek-V4.1-Flash/<case>/rerun_<k>/Fix-Agent/results | mean of Final Attempt | 2026-11-16 |
| ad37_deepseek_attempt_runs | 185 | DeepSeek-V4.1-Flash, runs with a result file over the 37 cases | AgentDefect/SelfHeal/DeepSeek-V4.1-Flash/<case>/rerun_<k>/Fix-Agent/results | count | 2026-11-16 |
| ad37_glm_succ_mean | 0.4595 | GLM-5.3, share of the 37 cases where the critic accepted and the test passed, mean over five runs | AgentDefect/SelfHeal/test_scores.csv | per run share of 37, mean | 2026-11-16 |
| ad37_glm_succ_2s | 0.0662 | GLM-5.3, two standard deviations of that share over five runs | AgentDefect/SelfHeal/test_scores.csv | 2 x sample sd | 2026-11-16 |
| ad37_glm_attempts | 1.05 | GLM-5.3, mean attempts per run over the 37 cases | AgentDefect/SelfHeal/GLM-5.3/<case>/rerun_<k>/Fix-Agent/results | mean of Final Attempt | 2026-11-16 |
| ad37_glm_attempt_runs | 185 | GLM-5.3, runs with a result file over the 37 cases | AgentDefect/SelfHeal/GLM-5.3/<case>/rerun_<k>/Fix-Agent/results | count | 2026-11-16 |
| ad37_runs_per_model | 185 | runs per model over the 37 cases, five per case | AgentDefect/SelfHeal/test_scores.csv | rows per model | 2026-11-16 |
| ad_runs_per_model | 180 | scored runs per model, five per case | AgentDefect/SelfHeal/test_scores.csv | in_table rows per model | 2026-11-16 |
| ad_cases | 36 | AgentDefect cases in our score tables | AgentDefect/SelfHeal/test_scores.csv | distinct in_table case | 2026-11-16 |
| ad_dropped_case | 79776520 | case left out of our score tables | AgentDefect/SelfHeal/test_scores.csv | in_table False | 2026-11-16 |
| ai_t6_Agentless_GPT4o_plausible | 12.00 | AgentIssue-Bench paper Table 6, Agentless with GPT-4o, plausible mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_Agentless_GPT4o_plausible_2s | 4.00 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_Agentless_GPT4o_correct | 3.33 | AgentIssue-Bench paper Table 6, Agentless with GPT-4o, correct mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_Agentless_GPT4o_correct_2s | 4.62 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_Agentless_GPT4o_loc_file | 27.82 | AgentIssue-Bench paper Table 6, Agentless with GPT-4o, loc_file mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_Agentless_GPT4o_loc_file_2s | 5.51 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_Agentless_GPT4o_loc_fn | 12.99 | AgentIssue-Bench paper Table 6, Agentless with GPT-4o, loc_fn mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_Agentless_GPT4o_loc_fn_2s | 2.78 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_Agentless_Claude35S_plausible | 12.00 | AgentIssue-Bench paper Table 6, Agentless with Claude-3.5-S, plausible mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_Agentless_Claude35S_plausible_2s | 0.00 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_Agentless_Claude35S_correct | 4.00 | AgentIssue-Bench paper Table 6, Agentless with Claude-3.5-S, correct mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_Agentless_Claude35S_correct_2s | 0.00 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_Agentless_Claude35S_loc_file | 27.35 | AgentIssue-Bench paper Table 6, Agentless with Claude-3.5-S, loc_file mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_Agentless_Claude35S_loc_file_2s | 0.00 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_Agentless_Claude35S_loc_fn | 17.50 | AgentIssue-Bench paper Table 6, Agentless with Claude-3.5-S, loc_fn mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_Agentless_Claude35S_loc_fn_2s | 0.00 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_AutoCodeRover_GPT4o_plausible | 7.33 | AgentIssue-Bench paper Table 6, AutoCodeRover with GPT-4o, plausible mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_AutoCodeRover_GPT4o_plausible_2s | 2.31 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_AutoCodeRover_GPT4o_correct | 1.33 | AgentIssue-Bench paper Table 6, AutoCodeRover with GPT-4o, correct mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_AutoCodeRover_GPT4o_correct_2s | 2.31 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_AutoCodeRover_GPT4o_loc_file | 22.07 | AgentIssue-Bench paper Table 6, AutoCodeRover with GPT-4o, loc_file mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_AutoCodeRover_GPT4o_loc_file_2s | 7.21 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_AutoCodeRover_GPT4o_loc_fn | 14.77 | AgentIssue-Bench paper Table 6, AutoCodeRover with GPT-4o, loc_fn mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_AutoCodeRover_GPT4o_loc_fn_2s | 2.62 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_AutoCodeRover_Claude35S_plausible | 12.67 | AgentIssue-Bench paper Table 6, AutoCodeRover with Claude-3.5-S, plausible mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_AutoCodeRover_Claude35S_plausible_2s | 6.11 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_AutoCodeRover_Claude35S_correct | 4.67 | AgentIssue-Bench paper Table 6, AutoCodeRover with Claude-3.5-S, correct mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_AutoCodeRover_Claude35S_correct_2s | 2.31 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_AutoCodeRover_Claude35S_loc_file | 25.81 | AgentIssue-Bench paper Table 6, AutoCodeRover with Claude-3.5-S, loc_file mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_AutoCodeRover_Claude35S_loc_file_2s | 11.43 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_AutoCodeRover_Claude35S_loc_fn | 19.18 | AgentIssue-Bench paper Table 6, AutoCodeRover with Claude-3.5-S, loc_fn mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_AutoCodeRover_Claude35S_loc_fn_2s | 5.54 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_SWEagent_GPT4o_plausible | 0.67 | AgentIssue-Bench paper Table 6, SWE-agent with GPT-4o, plausible mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_SWEagent_GPT4o_plausible_2s | 2.31 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_SWEagent_GPT4o_correct | 0.67 | AgentIssue-Bench paper Table 6, SWE-agent with GPT-4o, correct mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_SWEagent_GPT4o_correct_2s | 2.31 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_SWEagent_GPT4o_loc_file | 11.67 | AgentIssue-Bench paper Table 6, SWE-agent with GPT-4o, loc_file mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_SWEagent_GPT4o_loc_file_2s | 5.17 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_SWEagent_GPT4o_loc_fn | 4.22 | AgentIssue-Bench paper Table 6, SWE-agent with GPT-4o, loc_fn mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_SWEagent_GPT4o_loc_fn_2s | 4.07 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_SWEagent_Claude35S_plausible | 2.00 | AgentIssue-Bench paper Table 6, SWE-agent with Claude-3.5-S, plausible mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_SWEagent_Claude35S_plausible_2s | 0.00 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_SWEagent_Claude35S_correct | 2.00 | AgentIssue-Bench paper Table 6, SWE-agent with Claude-3.5-S, correct mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_SWEagent_Claude35S_correct_2s | 0.00 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_SWEagent_Claude35S_loc_file | 9.52 | AgentIssue-Bench paper Table 6, SWE-agent with Claude-3.5-S, loc_file mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_SWEagent_Claude35S_loc_file_2s | 5.24 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_SWEagent_Claude35S_loc_fn | 6.78 | AgentIssue-Bench paper Table 6, SWE-agent with Claude-3.5-S, loc_fn mean over three runs | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t6_SWEagent_Claude35S_loc_fn_2s | 2.59 | same, two sigma | AgentIssue-Bench paper arXiv 2505.20749, Table 6 | copied | 2026-11-16 |
| ai_t2_Agentless_GPT4o_cost | 0.65 | AgentIssue-Bench paper Table 2, Agentless with GPT-4o, average cost in dollars | AgentIssue-Bench paper arXiv 2505.20749, Table 2 | copied | 2026-11-16 |
| ai_t2_Agentless_Claude35S_cost | 0.33 | AgentIssue-Bench paper Table 2, Agentless with Claude-3.5-S, average cost in dollars | AgentIssue-Bench paper arXiv 2505.20749, Table 2 | copied | 2026-11-16 |
| ai_t2_AutoCodeRover_GPT4o_cost | 0.23 | AgentIssue-Bench paper Table 2, AutoCodeRover with GPT-4o, average cost in dollars | AgentIssue-Bench paper arXiv 2505.20749, Table 2 | copied | 2026-11-16 |
| ai_t2_AutoCodeRover_Claude35S_cost | 0.05 | AgentIssue-Bench paper Table 2, AutoCodeRover with Claude-3.5-S, average cost in dollars | AgentIssue-Bench paper arXiv 2505.20749, Table 2 | copied | 2026-11-16 |
| ai_t2_SWEagent_GPT4o_cost | 1.15 | AgentIssue-Bench paper Table 2, SWE-agent with GPT-4o, average cost in dollars | AgentIssue-Bench paper arXiv 2505.20749, Table 2 | copied | 2026-11-16 |
| ai_t2_SWEagent_Claude35S_cost | 0.57 | AgentIssue-Bench paper Table 2, SWE-agent with Claude-3.5-S, average cost in dollars | AgentIssue-Bench paper arXiv 2505.20749, Table 2 | copied | 2026-11-16 |
| ai_issues | 50 | AgentIssue-Bench issues | AgentIssue-Bench paper | '50 agent issues' | 2026-11-16 |
| ai_sh_plaus_5 | 18.80 | SelfHeal gpt-oss-120b, percent of the 50 issues whose returned code passes the shipped test, mean over five runs | AgentIssue-Bench/SelfHeal/test_scores.csv, shipped rows | per run percent, mean | 2026-11-16 |
| ai_sh_plaus_5_2s | 6.69 | same, two sigma over five runs | AgentIssue-Bench/SelfHeal/test_scores.csv, shipped rows | 2 x sample sd | 2026-11-16 |
| ai_sh_plaus_3 | 20.00 | same, mean over runs 1 to 3 | AgentIssue-Bench/SelfHeal/test_scores.csv, shipped rows | per run percent, mean | 2026-11-16 |
| ai_sh_plaus_3_2s | 8.00 | same, two sigma over runs 1 to 3 | AgentIssue-Bench/SelfHeal/test_scores.csv, shipped rows | 2 x sample sd | 2026-11-16 |
| ai_sh_plaus_run1 | 20 | percent of issues passing in run 1 | AgentIssue-Bench/SelfHeal/test_scores.csv, shipped rows | count / 50 x 100 | 2026-11-16 |
| ai_sh_plaus_run2 | 16 | percent of issues passing in run 2 | AgentIssue-Bench/SelfHeal/test_scores.csv, shipped rows | count / 50 x 100 | 2026-11-16 |
| ai_sh_plaus_run3 | 24 | percent of issues passing in run 3 | AgentIssue-Bench/SelfHeal/test_scores.csv, shipped rows | count / 50 x 100 | 2026-11-16 |
| ai_sh_plaus_run4 | 18 | percent of issues passing in run 4 | AgentIssue-Bench/SelfHeal/test_scores.csv, shipped rows | count / 50 x 100 | 2026-11-16 |
| ai_sh_plaus_run5 | 16 | percent of issues passing in run 5 | AgentIssue-Bench/SelfHeal/test_scores.csv, shipped rows | count / 50 x 100 | 2026-11-16 |
| ai_sh_passing_runs | 47 | runs whose returned code passed the shipped test, of 250 | AgentIssue-Bench/SelfHeal/test_scores.csv, shipped rows | final_test_passed | 2026-11-16 |
| ai_sh_runs | 250 | SelfHeal runs on AgentIssue-Bench with gpt-oss-120b | AgentIssue-Bench/SelfHeal/test_scores.csv, shipped rows | rows | 2026-11-16 |
| ai_sh_passing_in_null_issues | 41 | of the passing runs, those in issues whose original code passes the test in all five runs | AgentIssue-Bench/SelfHeal/test_scores.csv, shipped rows | with case_check shipped_negative records | 2026-11-16 |
| ai_null_issues | 10 | issues whose original code passes the shipped test in all five runs | AgentIssue-Bench/case_check/gpt-oss-120b/<tag>/shipped_negative_<k> | all five passed | 2026-11-16 |
| ai_sh_success | 9 | runs the critic accepted and whose code passed, of 250 | AgentIssue-Bench/SelfHeal/test_scores.csv, shipped rows | final_success | 2026-11-16 |
