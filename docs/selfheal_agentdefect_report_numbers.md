# Number registry, SelfHeal on AgentDefect

Rows written by `docs/selfheal_agentdefect_report_numbers.py`. The report is checked with

```
python3 ~/.claude/skills/number-check/scripts/check_numbers.py --registry docs/selfheal_agentdefect_report_numbers.md --ignore '^[0-9]\.[0-9](\.[0-9])?$' --ignore '^(2611\.09792|1603\.09326|2604\.17699)$' docs/selfheal_agentdefect_report.md
```

The ignore patterns skip section numbers and the three arXiv ids.

| name | value | what it counts | source file | how it is computed | date read |
|---|---|---|---|---|---|
| code_attempt_loop | 281 | line that sets three attempts | /data/wang/junh/githubs/SelfHeal/run_agent.py | line text | 2026-11-16 |
| code_verify_first | 204 | first docstring line of verify_api_usage, the critic's search tool | /data/wang/junh/githubs/SelfHeal/run_agent.py | line text | 2026-11-16 |
| code_verify_last | 229 | last line of verify_api_usage | /data/wang/junh/githubs/SelfHeal/run_agent.py | line text | 2026-11-16 |
| code_fixer_tools_first | 247 | first line of the fix agent's tool list | /data/wang/junh/githubs/SelfHeal/run_agent.py | line text | 2026-11-16 |
| code_fixer_agent | 254 | line that builds the fix agent | /data/wang/junh/githubs/SelfHeal/run_agent.py | line text | 2026-11-16 |
| code_fixer_stream_first | 325 | first line of the fix agent's run call | /data/wang/junh/githubs/SelfHeal/run_agent.py | line text | 2026-11-16 |
| code_fixer_stream_last | 328 | last line of the fix agent's run call | /data/wang/junh/githubs/SelfHeal/run_agent.py | line text | 2026-11-16 |
| code_success_line | 143 | line of AgentDefect score_tests.py that defines a success | AgentDefect/SelfHeal/code/score_tests.py | line text | 2026-11-16 |
| langgraph_limit_line | 31 | line of langgraph's _config.py that sets the default step limit | /data/wang/junh/envs/selfheal/lib/python3.10/site-packages/langgraph/_internal/_config.py | line text | 2026-11-16 |
| langgraph_default_limit | 10007 | langgraph 1.1.6 default recursion limit | /data/wang/junh/envs/selfheal/lib/python3.10/site-packages/langgraph/_internal/_config.py | value on line 31 | 2026-11-16 |
| setup_cases | 37 | AgentDefect case folders | AgentDefect/SelfHeal/inputs/fetch_record.json | case_folders | 2026-11-16 |
| setup_train_posts | 665 | training posts the fix rules need | AgentDefect/SelfHeal/inputs/fetch_record.json | train_ids | 2026-11-16 |
| setup_train_returned | 660 | training posts the Stack Exchange API returned | AgentDefect/SelfHeal/inputs/fetch_record.json | train_ids minus the length of train_missing | 2026-11-16 |
| setup_missing_post_1 | 75873494 | id of a training post the Stack Exchange API did not return | AgentDefect/SelfHeal/inputs/fetch_record.json | train_missing | 2026-11-16 |
| setup_missing_post_2 | 76646276 | id of a training post the Stack Exchange API did not return | AgentDefect/SelfHeal/inputs/fetch_record.json | train_missing | 2026-11-16 |
| setup_missing_post_3 | 79028921 | id of a training post the Stack Exchange API did not return | AgentDefect/SelfHeal/inputs/fetch_record.json | train_missing | 2026-11-16 |
| setup_missing_post_4 | 79277755 | id of a training post the Stack Exchange API did not return | AgentDefect/SelfHeal/inputs/fetch_record.json | train_missing | 2026-11-16 |
| setup_missing_post_5 | 79371473 | id of a training post the Stack Exchange API did not return | AgentDefect/SelfHeal/inputs/fetch_record.json | train_missing | 2026-11-16 |
| setup_train_missing | 5 | training posts the API did not return | AgentDefect/SelfHeal/inputs/fetch_record.json | train_missing | 2026-11-16 |
| setup_rules | 24 | fix rules built by SelfHeal's scripts | AgentDefect/SelfHeal/gpt-oss-120b/rules/fix_pattern_rules.csv | data rows | 2026-11-16 |
| setup_paper_patterns | 23 | fix patterns the SelfHeal paper states | SelfHeal paper arXiv 2604.17699 v1, section 3 | text "twenty-three fix patterns" | 2026-11-16 |
| setup_req_lists | 15 | distinct requirement lists over the cases | AgentDefect/SelfHeal/test_env_logs/list_<n>_install.json | list_<n> records without a letter suffix | 2026-11-16 |
| setup_arc_cap | 8000 | token cap ARC sets on replies that are not streamed | docs/selfheal_deployment.md section 2.2 | observed when GLM-5.3 replies stopped at the cap before the relay streamed | 2026-11-16 |
| ad_cases_scored | 36 | cases in the score tables | AgentDefect/SelfHeal/test_scores.csv | distinct case with in_table True | 2026-11-16 |
| ad_runs | 180 | gpt-oss-120b planned repetitions in the score tables, five per case | AgentDefect/SelfHeal/test_scores.csv | in_table rows of gpt-oss-120b | 2026-11-16 |
| ad_dropped_case | 79776520 | case left out of the score tables, needs Google and Tavily keys | AgentDefect/SelfHeal/test_scores.csv | case with in_table False | 2026-11-16 |
| ad_successes | 54 | runs ACCEPTED whose repair passed test.py | AgentDefect/SelfHeal/test_scores.csv | final_success True | 2026-11-16 |
| ad_cases_with_0 | 18 | cases with 0 successful runs of five | AgentDefect/SelfHeal/test_scores.csv | successes per case | 2026-11-16 |
| ad_cases_with_1 | 5 | cases with 1 successful runs of five | AgentDefect/SelfHeal/test_scores.csv | successes per case | 2026-11-16 |
| ad_cases_with_2 | 2 | cases with 2 successful runs of five | AgentDefect/SelfHeal/test_scores.csv | successes per case | 2026-11-16 |
| ad_cases_with_3 | 3 | cases with 3 successful runs of five | AgentDefect/SelfHeal/test_scores.csv | successes per case | 2026-11-16 |
| ad_cases_with_4 | 4 | cases with 4 successful runs of five | AgentDefect/SelfHeal/test_scores.csv | successes per case | 2026-11-16 |
| ad_cases_with_5 | 4 | cases with 5 successful runs of five | AgentDefect/SelfHeal/test_scores.csv | successes per case | 2026-11-16 |
| ad_accepted_pass | 54 | runs with status ACCEPTED and test passed True | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| ad_accepted_fail | 84 | runs with status ACCEPTED and test passed False | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| ad_failed_pass | 0 | runs with status FAILED and test passed True | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| ad_failed_fail | 42 | runs with status FAILED and test passed False | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| ad_no_result | 0 | runs with status NO RESULT and test passed False | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| ad_test_passed | 54 | runs whose final code passed test.py, either status | AgentDefect/SelfHeal/test_scores.csv | final_test_passed True | 2026-11-16 |
| grp_fail_issues | 27 | cases whose original program gives the group 'fails without a fix' | AgentDefect/case_check/gpt-oss-120b/<case>/buggy_<k> | five runs of the original program | 2026-11-16 |
| grp_fail_runs | 135 | runs in cases of the group 'fails without a fix' | AgentDefect/SelfHeal/test_scores.csv | rows per group | 2026-11-16 |
| grp_fail_ap | 24 | runs of group 'fails without a fix' with status ACCEPTED and test passed True | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| grp_fail_af | 70 | runs of group 'fails without a fix' with status ACCEPTED and test passed False | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| grp_fail_fp | 0 | runs of group 'fails without a fix' with status FAILED and test passed True | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| grp_fail_ff | 41 | runs of group 'fails without a fix' with status FAILED and test passed False | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| grp_fail_nr | 0 | runs of group 'fails without a fix' with status NO RESULT and test passed False | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| grp_null_issues | 8 | cases whose original program gives the group 'passes without a fix' | AgentDefect/case_check/gpt-oss-120b/<case>/buggy_<k> | five runs of the original program | 2026-11-16 |
| grp_null_runs | 40 | runs in cases of the group 'passes without a fix' | AgentDefect/SelfHeal/test_scores.csv | rows per group | 2026-11-16 |
| grp_null_ap | 28 | runs of group 'passes without a fix' with status ACCEPTED and test passed True | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| grp_null_af | 11 | runs of group 'passes without a fix' with status ACCEPTED and test passed False | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| grp_null_fp | 0 | runs of group 'passes without a fix' with status FAILED and test passed True | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| grp_null_ff | 1 | runs of group 'passes without a fix' with status FAILED and test passed False | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| grp_null_nr | 0 | runs of group 'passes without a fix' with status NO RESULT and test passed False | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| grp_mixed_issues | 1 | cases whose original program gives the group 'unstable' | AgentDefect/case_check/gpt-oss-120b/<case>/buggy_<k> | five runs of the original program | 2026-11-16 |
| grp_mixed_runs | 5 | runs in cases of the group 'unstable' | AgentDefect/SelfHeal/test_scores.csv | rows per group | 2026-11-16 |
| grp_mixed_ap | 2 | runs of group 'unstable' with status ACCEPTED and test passed True | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| grp_mixed_af | 3 | runs of group 'unstable' with status ACCEPTED and test passed False | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| grp_mixed_fp | 0 | runs of group 'unstable' with status FAILED and test passed True | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| grp_mixed_ff | 0 | runs of group 'unstable' with status FAILED and test passed False | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| grp_mixed_nr | 0 | runs of group 'unstable' with status NO RESULT and test passed False | AgentDefect/SelfHeal/test_scores.csv | final_status, final_test_passed | 2026-11-16 |
| cause0_runs | 0 | runs with cause 'no repair' | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause0_acc | 0 | runs with cause 'no repair', status ACCEPTED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause0_fail | 0 | runs with cause 'no repair', status FAILED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause0_nores | 0 | runs with cause 'no repair', status NO RESULT | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause1_runs | 40 | runs with cause 'test passes without a fix' | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause1_acc | 39 | runs with cause 'test passes without a fix', status ACCEPTED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause1_fail | 1 | runs with cause 'test passes without a fix', status FAILED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause1_nores | 0 | runs with cause 'test passes without a fix', status NO RESULT | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause2_runs | 5 | runs with cause 'test unstable' | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause2_acc | 5 | runs with cause 'test unstable', status ACCEPTED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause2_fail | 0 | runs with cause 'test unstable', status FAILED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause2_nores | 0 | runs with cause 'test unstable', status NO RESULT | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause3_runs | 24 | runs with cause 'test passed' | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause3_acc | 24 | runs with cause 'test passed', status ACCEPTED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause3_fail | 0 | runs with cause 'test passed', status FAILED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause3_nores | 0 | runs with cause 'test passed', status NO RESULT | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause4_runs | 0 | runs with cause 'did not get every file the fix touches' | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause4_acc | 0 | runs with cause 'did not get every file the fix touches', status ACCEPTED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause4_fail | 0 | runs with cause 'did not get every file the fix touches', status FAILED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause4_nores | 0 | runs with cause 'did not get every file the fix touches', status NO RESULT | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause5_runs | 0 | runs with cause 'left out a file it got' | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause5_acc | 0 | runs with cause 'left out a file it got', status ACCEPTED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause5_fail | 0 | runs with cause 'left out a file it got', status FAILED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause5_nores | 0 | runs with cause 'left out a file it got', status NO RESULT | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause6_runs | 0 | runs with cause 'patch did not apply' | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause6_acc | 0 | runs with cause 'patch did not apply', status ACCEPTED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause6_fail | 0 | runs with cause 'patch did not apply', status FAILED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause6_nores | 0 | runs with cause 'patch did not apply', status NO RESULT | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause7_runs | 0 | runs with cause 'changed fewer source files than the fix' | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause7_acc | 0 | runs with cause 'changed fewer source files than the fix', status ACCEPTED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause7_fail | 0 | runs with cause 'changed fewer source files than the fix', status FAILED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause7_nores | 0 | runs with cause 'changed fewer source files than the fix', status NO RESULT | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause8_runs | 63 | runs with cause 'failed like the null patch' | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause8_acc | 52 | runs with cause 'failed like the null patch', status ACCEPTED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause8_fail | 11 | runs with cause 'failed like the null patch', status FAILED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause8_nores | 0 | runs with cause 'failed like the null patch', status NO RESULT | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause9_runs | 48 | runs with cause 'failed otherwise' | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause9_acc | 18 | runs with cause 'failed otherwise', status ACCEPTED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause9_fail | 30 | runs with cause 'failed otherwise', status FAILED | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| cause9_nores | 0 | runs with cause 'failed otherwise', status NO RESULT | AgentDefect records, rules of analyze_multifile.py | cause, status | 2026-11-16 |
| sep_failures | 111 | failing runs with a repair in cases that fail without a fix | AgentDefect records | cause other than test passed and no repair | 2026-11-16 |
| sep_accepted | 94 | runs ACCEPTED in cases that fail without a fix | AgentDefect/SelfHeal/test_scores.csv | final_status | 2026-11-16 |
| sep_rejected | 41 | runs FAILED in cases that fail without a fix | AgentDefect/SelfHeal/test_scores.csv | final_status | 2026-11-16 |
| sep_successes | 24 | successes in cases that fail without a fix | AgentDefect/SelfHeal/test_scores.csv | final_success | 2026-11-16 |
| null_successes | 28 | successes in cases that pass without a fix | AgentDefect/SelfHeal/test_scores.csv | final_success | 2026-11-16 |
| mixed_successes | 2 | successes in unstable cases | AgentDefect/SelfHeal/test_scores.csv | final_success | 2026-11-16 |
| fix_one_issues | 27 | cases that fail without a fix whose fix touches 'one' source files | AgentDefect.zip run_buggy.py and run_fixed.py | text differs | 2026-11-16 |
| fix_one_runs | 135 | runs of those cases | AgentDefect/SelfHeal/test_scores.csv | rows | 2026-11-16 |
| fix_one_got | 135 | of those runs, SelfHeal received every fix file | AgentDefect records | the whole program is SelfHeal's input | 2026-11-16 |
| fix_one_passed | 24 | of those runs, test.py passed | AgentDefect/SelfHeal/<model>/<case>/rerun_<k>/test/test_record.json | passed | 2026-11-16 |
| fix_two_to_seven_issues | 0 | cases that fail without a fix whose fix touches 'two to seven' source files | AgentDefect.zip run_buggy.py and run_fixed.py | text differs | 2026-11-16 |
| fix_two_to_seven_runs | 0 | runs of those cases | AgentDefect/SelfHeal/test_scores.csv | rows | 2026-11-16 |
| fix_two_to_seven_got | 0 | of those runs, SelfHeal received every fix file | AgentDefect records | the whole program is SelfHeal's input | 2026-11-16 |
| fix_two_to_seven_passed | 0 | of those runs, test.py passed | AgentDefect/SelfHeal/<model>/<case>/rerun_<k>/test/test_record.json | passed | 2026-11-16 |
| fix_unknown_issues | 0 | cases that fail without a fix whose fix touches 'unknown' source files | AgentDefect.zip run_buggy.py and run_fixed.py | text differs | 2026-11-16 |
| fix_unknown_runs | 0 | runs of those cases | AgentDefect/SelfHeal/test_scores.csv | rows | 2026-11-16 |
| fix_unknown_got | 0 | of those runs, SelfHeal received every fix file | AgentDefect records | the whole program is SelfHeal's input | 2026-11-16 |
| fix_unknown_passed | 0 | of those runs, test.py passed | AgentDefect/SelfHeal/<model>/<case>/rerun_<k>/test/test_record.json | passed | 2026-11-16 |
| fix_none_issues | 0 | cases that fail without a fix whose fix touches 'none' source files | AgentDefect.zip run_buggy.py and run_fixed.py | text differs | 2026-11-16 |
| fix_none_runs | 0 | runs of those cases | AgentDefect/SelfHeal/test_scores.csv | rows | 2026-11-16 |
| fix_none_got | 0 | of those runs, SelfHeal received every fix file | AgentDefect records | the whole program is SelfHeal's input | 2026-11-16 |
| fix_none_passed | 0 | of those runs, test.py passed | AgentDefect/SelfHeal/<model>/<case>/rerun_<k>/test/test_record.json | passed | 2026-11-16 |
| chf_every_cases | 23 | cases that fail without a fix with a run whose repair changed 'every' of the fix's functions | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | code_units of score_tests.py | 2026-11-16 |
| chf_every_runs | 115 | runs whose repair changed 'every' of the functions the fixed program changes | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | code_units of score_tests.py | 2026-11-16 |
| chf_every_passed | 18 | of those runs, test passed | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | final_test_passed | 2026-11-16 |
| chf_every_succ | 18 | of those runs, successes | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | final_success | 2026-11-16 |
| chf_some_cases | 4 | cases that fail without a fix with a run whose repair changed 'some' of the fix's functions | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | code_units of score_tests.py | 2026-11-16 |
| chf_some_runs | 19 | runs whose repair changed 'some' of the functions the fixed program changes | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | code_units of score_tests.py | 2026-11-16 |
| chf_some_passed | 6 | of those runs, test passed | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | final_test_passed | 2026-11-16 |
| chf_some_succ | 6 | of those runs, successes | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | final_success | 2026-11-16 |
| chf_none_cases | 0 | cases that fail without a fix with a run whose repair changed 'none' of the fix's functions | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | code_units of score_tests.py | 2026-11-16 |
| chf_none_runs | 0 | runs whose repair changed 'none' of the functions the fixed program changes | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | code_units of score_tests.py | 2026-11-16 |
| chf_none_passed | 0 | of those runs, test passed | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | final_test_passed | 2026-11-16 |
| chf_none_succ | 0 | of those runs, successes | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | final_success | 2026-11-16 |
| chf_no_fix_units_cases | 0 | cases that fail without a fix with a run whose repair changed 'no_fix_units' of the fix's functions | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | code_units of score_tests.py | 2026-11-16 |
| chf_no_fix_units_runs | 0 | runs whose repair changed 'no_fix_units' of the functions the fixed program changes | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | code_units of score_tests.py | 2026-11-16 |
| chf_no_fix_units_passed | 0 | of those runs, test passed | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | final_test_passed | 2026-11-16 |
| chf_no_fix_units_succ | 0 | of those runs, successes | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | final_success | 2026-11-16 |
| chf_unknown_cases | 1 | cases that fail without a fix with a run whose repair changed 'unknown' of the fix's functions | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | code_units of score_tests.py | 2026-11-16 |
| chf_unknown_runs | 1 | runs whose repair changed 'unknown' of the functions the fixed program changes | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | code_units of score_tests.py | 2026-11-16 |
| chf_unknown_passed | 0 | of those runs, test passed | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | final_test_passed | 2026-11-16 |
| chf_unknown_succ | 0 | of those runs, successes | AgentDefect.zip run_buggy.py and run_fixed.py, AgentDefect/SelfHeal/test_scores.csv final_changed_functions | final_success | 2026-11-16 |
| ex_case | 77099194 | case used as the worked example of the three sets | AgentDefect.zip | case folder name | 2026-11-16 |
| ex_k_buggy | 1 | rows the buggy program retrieves | AgentDefect.zip run_buggy.py | search_kwargs k | 2026-11-16 |
| ex_k_fixed | 12 | rows the authors' fixed program retrieves | AgentDefect.zip run_fixed.py | search_kwargs k | 2026-11-16 |
| ex_buggy_runs | 5 | calibration runs of the buggy program for the example case | AgentDefect/case_check/gpt-oss-120b/77099194/buggy_<k>/test_record.json | count | 2026-11-16 |
| ex_buggy_passed | 0 | of those, passed | AgentDefect/case_check/gpt-oss-120b/77099194/buggy_<k>/test_record.json | passed | 2026-11-16 |
| ex_rep1_lines | 39 | lines repair 1 adds or removes against the buggy program | AgentDefect/SelfHeal/gpt-oss-120b/77099194/rerun_1/test/run_fixed.py | unified diff, zero context | 2026-11-16 |
| ex_rep1_k | 5 | rows repair 1 retrieves | AgentDefect/SelfHeal/gpt-oss-120b/77099194/rerun_1/test/run_fixed.py | search_kwargs k or its default | 2026-11-16 |
| ex_rep1_status | ACCEPTED | critic's final verdict on repair 1 | AgentDefect/SelfHeal/test_scores.csv | final_status | 2026-11-16 |
| ex_rep1_passed | 0 | repair 1 passed the test | AgentDefect/SelfHeal/test_scores.csv | final_test_passed | 2026-11-16 |
| ex_rep2_lines | 43 | lines repair 2 adds or removes against the buggy program | AgentDefect/SelfHeal/gpt-oss-120b/77099194/rerun_2/test/run_fixed.py | unified diff, zero context | 2026-11-16 |
| ex_rep2_k | 5 | rows repair 2 retrieves | AgentDefect/SelfHeal/gpt-oss-120b/77099194/rerun_2/test/run_fixed.py | search_kwargs k or its default | 2026-11-16 |
| ex_rep2_status | ACCEPTED | critic's final verdict on repair 2 | AgentDefect/SelfHeal/test_scores.csv | final_status | 2026-11-16 |
| ex_rep2_passed | 0 | repair 2 passed the test | AgentDefect/SelfHeal/test_scores.csv | final_test_passed | 2026-11-16 |
| ex_rep3_lines | 40 | lines repair 3 adds or removes against the buggy program | AgentDefect/SelfHeal/gpt-oss-120b/77099194/rerun_3/test/run_fixed.py | unified diff, zero context | 2026-11-16 |
| ex_rep3_k | 10 | rows repair 3 retrieves | AgentDefect/SelfHeal/gpt-oss-120b/77099194/rerun_3/test/run_fixed.py | search_kwargs k or its default | 2026-11-16 |
| ex_rep3_status | ACCEPTED | critic's final verdict on repair 3 | AgentDefect/SelfHeal/test_scores.csv | final_status | 2026-11-16 |
| ex_rep3_passed | 1 | repair 3 passed the test | AgentDefect/SelfHeal/test_scores.csv | final_test_passed | 2026-11-16 |
| ex_rep4_lines | 43 | lines repair 4 adds or removes against the buggy program | AgentDefect/SelfHeal/gpt-oss-120b/77099194/rerun_4/test/run_fixed.py | unified diff, zero context | 2026-11-16 |
| ex_rep4_k | 10 | rows repair 4 retrieves | AgentDefect/SelfHeal/gpt-oss-120b/77099194/rerun_4/test/run_fixed.py | search_kwargs k or its default | 2026-11-16 |
| ex_rep4_status | ACCEPTED | critic's final verdict on repair 4 | AgentDefect/SelfHeal/test_scores.csv | final_status | 2026-11-16 |
| ex_rep4_passed | 1 | repair 4 passed the test | AgentDefect/SelfHeal/test_scores.csv | final_test_passed | 2026-11-16 |
| ex_rep5_lines | 40 | lines repair 5 adds or removes against the buggy program | AgentDefect/SelfHeal/gpt-oss-120b/77099194/rerun_5/test/run_fixed.py | unified diff, zero context | 2026-11-16 |
| ex_rep5_k | 10 | rows repair 5 retrieves | AgentDefect/SelfHeal/gpt-oss-120b/77099194/rerun_5/test/run_fixed.py | search_kwargs k or its default | 2026-11-16 |
| ex_rep5_status | ACCEPTED | critic's final verdict on repair 5 | AgentDefect/SelfHeal/test_scores.csv | final_status | 2026-11-16 |
| ex_rep5_passed | 1 | repair 5 passed the test | AgentDefect/SelfHeal/test_scores.csv | final_test_passed | 2026-11-16 |
| ex_lines_about | 40 | lines each repair changed, rounded, the five repairs changed 39 to 43 | AgentDefect/SelfHeal/gpt-oss-120b/77099194/rerun_<k>/test/run_fixed.py | ex_rep<k>_lines, all within 35 to 45 | 2026-11-16 |
| v1_fail_runs | 135 | runs with a result file, fail cases | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_fail_acc1 | 76 | runs ACCEPTED at attempt 1 | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_fail_acc1_succ | 20 | successes among them | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines, final_success of test_scores.csv | 2026-11-16 |
| v1_fail_rej1 | 59 | runs rejected at attempt 1 | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_fail_rej1_succ | 4 | successes among them | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines, final_success of test_scores.csv | 2026-11-16 |
| v1_fail_share | 0.56 | attempt 1 duration over all attempts' duration, summed over runs | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_fail_after | 0.44 | attempts 2 and 3 duration over all attempts' duration | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_fail_acc_any | 94 | runs ACCEPTED at any attempt | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_fail_rejected | 41 | runs FAILED, rejected at every attempt | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_fail_stop1 | 20 | successes if SelfHeal stopped after attempt 1 | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_fail_stop2 | 23 | successes if SelfHeal stopped after attempt 2 | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_fail_stop3 | 24 | successes if SelfHeal stopped after attempt 3 | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_fail_rej1_acc_at2 | 3 | successes accepted at attempt 2 | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_all_runs | 180 | runs with a result file, all cases | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_all_acc1 | 112 | runs ACCEPTED at attempt 1 | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_all_acc1_succ | 46 | successes among them | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines, final_success of test_scores.csv | 2026-11-16 |
| v1_all_rej1 | 68 | runs rejected at attempt 1 | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_all_rej1_succ | 8 | successes among them | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines, final_success of test_scores.csv | 2026-11-16 |
| v1_all_share | 0.59 | attempt 1 duration over all attempts' duration, summed over runs | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_all_after | 0.41 | attempts 2 and 3 duration over all attempts' duration | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_all_acc_any | 138 | runs ACCEPTED at any attempt | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_all_rejected | 42 | runs FAILED, rejected at every attempt | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_all_stop1 | 46 | successes if SelfHeal stopped after attempt 1 | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_all_stop2 | 51 | successes if SelfHeal stopped after attempt 2 | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_all_stop3 | 54 | successes if SelfHeal stopped after attempt 3 | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| v1_all_rej1_acc_at2 | 5 | successes accepted at attempt 2 | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/Fix-Agent/results/<case>_result.txt | Status, Final Attempt, Duration lines | 2026-11-16 |
| ts_fail_runs | 135 | runs with both a repair time and a test time, fail cases | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/run_record.json and test/test_record.json | both files present, test record has seconds | 2026-11-16 |
| ts_fail_repair_h | 3.58 | repair hours | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/run_record.json and test/test_record.json | sum of run_record attempts seconds / 3600 | 2026-11-16 |
| ts_fail_repair_min_run | 1.59 | SelfHeal minutes per run | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/run_record.json and test/test_record.json | sum of run_record attempts seconds / 60 / runs | 2026-11-16 |
| ts_fail_test_min_run | 0.30 | test minutes per run | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/run_record.json and test/test_record.json | sum of test_record seconds / 60 / runs | 2026-11-16 |
| ts_fail_test_h | 0.67 | test hours | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/run_record.json and test/test_record.json | sum of test_record seconds / 3600 | 2026-11-16 |
| ts_fail_share | 0.158 | test share of repair plus test time | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/run_record.json and test/test_record.json | test / (repair + test) | 2026-11-16 |
| ts_all_runs | 180 | runs with both a repair time and a test time, all cases | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/run_record.json and test/test_record.json | both files present, test record has seconds | 2026-11-16 |
| ts_all_repair_h | 4.24 | repair hours | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/run_record.json and test/test_record.json | sum of run_record attempts seconds / 3600 | 2026-11-16 |
| ts_all_repair_min_run | 1.41 | SelfHeal minutes per run | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/run_record.json and test/test_record.json | sum of run_record attempts seconds / 60 / runs | 2026-11-16 |
| ts_all_test_min_run | 0.31 | test minutes per run | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/run_record.json and test/test_record.json | sum of test_record seconds / 60 / runs | 2026-11-16 |
| ts_all_test_h | 0.93 | test hours | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/run_record.json and test/test_record.json | sum of test_record seconds / 3600 | 2026-11-16 |
| ts_all_share | 0.180 | test share of repair plus test time | AgentDefect/SelfHeal/gpt-oss-120b/<case>/rerun_<k>/run_record.json and test/test_record.json | test / (repair + test) | 2026-11-16 |
| s_gpt_searches | 541 | gpt-oss-120b searches | AgentDefect/SelfHeal/gpt-oss-120b/**/relay_log_run_agent.jsonl without _not_streamed | web_search and verify_api_usage tool replies, kept and moved-aside runs | 2026-11-16 |
| s_gpt_fail | 0.022 | gpt-oss-120b share of searches with 'Search error' | AgentDefect/SelfHeal/gpt-oss-120b/**/relay_log_run_agent.jsonl without _not_streamed | web_search and verify_api_usage tool replies, kept and moved-aside runs | 2026-11-16 |
| s_gpt_median | 1 | gpt-oss-120b median searches per run with a search | AgentDefect/SelfHeal/gpt-oss-120b/**/relay_log_run_agent.jsonl without _not_streamed | web_search and verify_api_usage tool replies, kept and moved-aside runs | 2026-11-16 |
| s_gpt_max | 41 | gpt-oss-120b most searches in one run | AgentDefect/SelfHeal/gpt-oss-120b/**/relay_log_run_agent.jsonl without _not_streamed | web_search and verify_api_usage tool replies, kept and moved-aside runs | 2026-11-16 |
| s_gpt_runs_err | 0.08 | gpt-oss-120b share of runs with a failed search | AgentDefect/SelfHeal/gpt-oss-120b/**/relay_log_run_agent.jsonl without _not_streamed | web_search and verify_api_usage tool replies, kept and moved-aside runs | 2026-11-16 |
| s_gpt_expected | 0.07 | gpt-oss-120b share expected if each search fails independently at the model's rate | AgentDefect/SelfHeal/gpt-oss-120b/**/relay_log_run_agent.jsonl without _not_streamed | mean over runs of 1-(1-p)^n | 2026-11-16 |
| s_deepseek_searches | 3824 | DeepSeek-V4.1-Flash searches | AgentDefect/SelfHeal/DeepSeek-V4.1-Flash/**/relay_log_run_agent.jsonl without _not_streamed | web_search and verify_api_usage tool replies, kept and moved-aside runs | 2026-11-16 |
| s_deepseek_fail | 0.070 | DeepSeek-V4.1-Flash share of searches with 'Search error' | AgentDefect/SelfHeal/DeepSeek-V4.1-Flash/**/relay_log_run_agent.jsonl without _not_streamed | web_search and verify_api_usage tool replies, kept and moved-aside runs | 2026-11-16 |
| s_deepseek_median | 8 | DeepSeek-V4.1-Flash median searches per run with a search | AgentDefect/SelfHeal/DeepSeek-V4.1-Flash/**/relay_log_run_agent.jsonl without _not_streamed | web_search and verify_api_usage tool replies, kept and moved-aside runs | 2026-11-16 |
| s_deepseek_max | 207 | DeepSeek-V4.1-Flash most searches in one run | AgentDefect/SelfHeal/DeepSeek-V4.1-Flash/**/relay_log_run_agent.jsonl without _not_streamed | web_search and verify_api_usage tool replies, kept and moved-aside runs | 2026-11-16 |
| s_deepseek_runs_err | 0.16 | DeepSeek-V4.1-Flash share of runs with a failed search | AgentDefect/SelfHeal/DeepSeek-V4.1-Flash/**/relay_log_run_agent.jsonl without _not_streamed | web_search and verify_api_usage tool replies, kept and moved-aside runs | 2026-11-16 |
| s_deepseek_expected | 0.51 | DeepSeek-V4.1-Flash share expected if each search fails independently at the model's rate | AgentDefect/SelfHeal/DeepSeek-V4.1-Flash/**/relay_log_run_agent.jsonl without _not_streamed | mean over runs of 1-(1-p)^n | 2026-11-16 |
| s_glm_searches | 2269 | GLM-5.3 searches | AgentDefect/SelfHeal/GLM-5.3/**/relay_log_run_agent.jsonl without _not_streamed | web_search and verify_api_usage tool replies, kept and moved-aside runs | 2026-11-16 |
| s_glm_fail | 0.026 | GLM-5.3 share of searches with 'Search error' | AgentDefect/SelfHeal/GLM-5.3/**/relay_log_run_agent.jsonl without _not_streamed | web_search and verify_api_usage tool replies, kept and moved-aside runs | 2026-11-16 |
| s_glm_median | 7 | GLM-5.3 median searches per run with a search | AgentDefect/SelfHeal/GLM-5.3/**/relay_log_run_agent.jsonl without _not_streamed | web_search and verify_api_usage tool replies, kept and moved-aside runs | 2026-11-16 |
| s_glm_max | 59 | GLM-5.3 most searches in one run | AgentDefect/SelfHeal/GLM-5.3/**/relay_log_run_agent.jsonl without _not_streamed | web_search and verify_api_usage tool replies, kept and moved-aside runs | 2026-11-16 |
| s_glm_runs_err | 0.21 | GLM-5.3 share of runs with a failed search | AgentDefect/SelfHeal/GLM-5.3/**/relay_log_run_agent.jsonl without _not_streamed | web_search and verify_api_usage tool replies, kept and moved-aside runs | 2026-11-16 |
| s_glm_expected | 0.22 | GLM-5.3 share expected if each search fails independently at the model's rate | AgentDefect/SelfHeal/GLM-5.3/**/relay_log_run_agent.jsonl without _not_streamed | mean over runs of 1-(1-p)^n | 2026-11-16 |
| s_errors_all | 341 | search errors over the three models | relay logs of the three models | replies with 'Search error' | 2026-11-16 |
| s_errors_ddg | 341 | of those, a timeout on html.duckduckgo.com | relay logs of the three models | reply text | 2026-11-16 |
