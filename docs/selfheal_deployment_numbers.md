# Number registry, SelfHeal deployment report

Rows written by `docs/selfheal_deployment_numbers.py`. The report is checked with

```
python3 ~/.claude/skills/number-check/scripts/check_numbers.py --registry docs/selfheal_deployment_numbers.md --ignore '^7[6-9][0-9]{6},?$' --ignore '^[0-9]\.[0-9]{1,2}$' --ignore '^2[56][0-9]{2}\.[0-9]{5}$' --ignore '127\.0\.0\.1' docs/selfheal_deployment.md
```

The ignore patterns skip the eight digit AgentDefect case ids, section numbers and two part versions such as 3.11 and 1.9, the arXiv ids, and the address 127.0.0.1.

| name | value | what it counts | source file | how it is computed | date read |
|---|---|---|---|---|---|
| ad_cases | 37 | AgentDefect case folders | /data/wang/junh/githubs/SelfHeal/AgentDefect.zip | distinct second path parts | 2026-11-13 |
| ad_so_cases | 36 | AgentDefect cases from Stack Overflow | /data/wang/junh/githubs/SelfHeal/AgentDefect.zip | case folders other than hf-26 | 2026-11-13 |
| fp_rows | 754 | rows of fix-pattern.csv, the StackOverflow sheet of Fix Patterns.xlsx | AgentDefect/SelfHeal/inputs/fix-pattern.csv | row count | 2026-11-13 |
| fp_posts | 665 | distinct posts in fix-pattern.csv | AgentDefect/SelfHeal/inputs/fix-pattern.csv | distinct id | 2026-11-13 |
| fp_patterns | 24 | distinct Fix Pattern names in fix-pattern.csv | AgentDefect/SelfHeal/inputs/fix-pattern.csv | distinct Fix Pattern | 2026-11-13 |
| train_posts | 660 | training posts the Stack Exchange API returned | AgentDefect/SelfHeal/inputs/train_descriptions.csv | row count | 2026-11-13 |
| ad_summaries | 634 | post summaries per model in the AgentDefect rules step, the same for all three models | AgentDefect/SelfHeal/gpt-oss-120b/rules/id_summaries2.csv | distinct id, each model | 2026-11-13 |
| ad_excluded_posts | 31 | training posts left out because they are AgentDefect cases | AgentDefect/SelfHeal/inputs/fix-pattern.csv | posts minus summaries | 2026-11-13 |
| ad_rules | 24 | fix rules per model | AgentDefect/SelfHeal/gpt-oss-120b/rules/fix_pattern_rules.csv | row count, each model | 2026-11-13 |
| ad_reruns_per_model | 185 | kept SelfHeal reruns per model on AgentDefect, 37 cases times five | AgentDefect/SelfHeal/<model>/<case>/rerun_<k>/Fix-Agent/results | result files per model | 2026-11-13 |
| ad_reruns_total | 555 | kept SelfHeal reruns on AgentDefect, three models | AgentDefect/SelfHeal/<model>/<case>/rerun_<k>/Fix-Agent/results | result files | 2026-11-13 |
| ad_gptoss_accepted | 138 | gpt-oss-120b reruns SelfHeal marked ACCEPTED | AgentDefect/SelfHeal/gpt-oss-120b | Status line of result files | 2026-11-13 |
| ad_gptoss_failed | 47 | gpt-oss-120b reruns SelfHeal marked FAILED | AgentDefect/SelfHeal/gpt-oss-120b | Status line of result files | 2026-11-13 |
| ad_gptoss_search_failed | 10 | gpt-oss-120b reruns in _search_failed | AgentDefect/SelfHeal/gpt-oss-120b/_search_failed | rerun folders | 2026-11-13 |
| ad_gptoss_not_streamed | 185 | gpt-oss-120b reruns in _not_streamed | AgentDefect/SelfHeal/gpt-oss-120b/_not_streamed | rerun folders | 2026-11-13 |
| ad_gptoss_not_streamed_search_failed | 56 | gpt-oss-120b reruns in _not_streamed/_search_failed | AgentDefect/SelfHeal/gpt-oss-120b/_not_streamed/_search_failed | rerun folders | 2026-11-13 |
| ad_glm_search_failed | 40 | GLM-5.3 reruns in _search_failed | AgentDefect/SelfHeal/GLM-5.3/_search_failed | rerun folders | 2026-11-13 |
| ad_glm_outage | 28 | GLM-5.3 reruns in _outage | AgentDefect/SelfHeal/GLM-5.3/_outage | rerun folders | 2026-11-13 |
| ad_glm_not_streamed | 185 | GLM-5.3 reruns in _not_streamed | AgentDefect/SelfHeal/GLM-5.3/_not_streamed | rerun folders | 2026-11-13 |
| ad_glm_not_streamed_search_failed | 14 | GLM-5.3 reruns in _not_streamed/_search_failed | AgentDefect/SelfHeal/GLM-5.3/_not_streamed/_search_failed | rerun folders | 2026-11-13 |
| ad_glm_not_streamed_token_limit | 39 | GLM-5.3 reruns in _not_streamed/_token_limit | AgentDefect/SelfHeal/GLM-5.3/_not_streamed/_token_limit | rerun folders | 2026-11-13 |
| ad_ds_search_failed | 32 | DeepSeek-V4.1-Flash reruns in _search_failed | AgentDefect/SelfHeal/DeepSeek-V4.1-Flash/_search_failed | rerun folders | 2026-11-13 |
| ad_ds_stopped | 5 | DeepSeek-V4.1-Flash reruns in _stopped | AgentDefect/SelfHeal/DeepSeek-V4.1-Flash/_stopped | rerun folders | 2026-11-13 |
| ad_glm_tl_cut | 15 | GLM-5.3 reruns of the first attempt before streaming with at least one reply ended for length | AgentDefect/SelfHeal/GLM-5.3/_not_streamed/_token_limit/*/rerun_*/relay_log_run_agent.jsonl | finish_reason length | 2026-11-13 |
| ad_glm_summary_calls_ns | 635 | GLM-5.3 summary calls in the rules step before the streaming redo, one repeated after a reply ended for length | AgentDefect/SelfHeal/GLM-5.3/_not_streamed/rules/relay_log_extract_summary.jsonl | line count | 2026-11-13 |
| ad_glm_summary_calls | 634 | GLM-5.3 summary calls in the kept streamed rules step | AgentDefect/SelfHeal/GLM-5.3/rules/relay_log_extract_summary.jsonl | line count | 2026-11-13 |
| ad_calib_first | 13 | AgentDefect cases calibrated first, departures 3 and 10 | AgentDefect/SelfHeal/code/test_repairs.py | CALIB_FIRST | 2026-11-13 |
| ad_calib_changed | 11 | AgentDefect cases whose environment, fixture or test was changed, departure 3 | AgentDefect/SelfHeal/code/test_repairs.py | CALIB_FIRST without the two Ollama cases 79149108 and 79638234 | 2026-11-13 |
| ad_calib_rest | 23 | AgentDefect cases in the score tables calibrated after the plan audit | AgentDefect/SelfHeal/code/test_repairs.py | case_ids minus CALIB_LEFT_OUT minus CALIB_FIRST | 2026-11-13 |
| ad_audit_model_replaced | 6 | tested repairs whose own chat model the relay served with the rerun's ARC model | AgentDefect/SelfHeal/audit_models_read.csv | row count | 2026-11-13 |
| ad_audit_model_replaced_pass | 4 | of those, repairs whose test passed | AgentDefect/SelfHeal/audit_models_read.csv | test_passed True | 2026-11-13 |
| audit_search_distinct | 42 | distinct flagged search results, both datasets, read by hand | AgentDefect/SelfHeal/audit_search_read.csv | row count | 2026-11-13 |
| audit_search_ai_hits | 16 | flagged search results in AgentIssue-Bench reruns | AgentDefect/SelfHeal/audit_search_read.csv | sum of hits | 2026-11-13 |
| arc_bad_gateway | 502 | HTTP status of the one GLM-5.3 call without streamed pieces, 77385587 rerun 2 line 2 | AgentDefect/SelfHeal/GLM-5.3/77385587/rerun_2/relay_log_run_agent.jsonl | status field | 2026-11-13 |
| arc_method_not_allowed | 405 | HTTP status ARC returns for the legacy /v1/completions endpoint | AgentDefect/SelfHeal/*/76897509/rerun_*/test/relay_log_test.jsonl | status field of /v1/completions calls | 2026-11-13 |
| arc_cap | 8000 | token cap ARC sets on replies that are not streamed | AgentDefect/SelfHeal/code/relay.py | module docstring | 2026-11-13 |
| ad_lists | 15 | different requirement lists of the 37 cases | AgentDefect/SelfHeal/code/test_repairs.py | LISTS | 2026-11-13 |
| ad_pins | 451 | different pins over the requirement lists | AgentDefect/SelfHeal/code/test_repairs.py | union of requirements over LISTS | 2026-11-13 |
| ad_envs | 17 | test environments, the 15 lists plus list_1b and list_1c | AgentDefect/SelfHeal/test_env_logs/list_*_install.json | install records | 2026-11-13 |
| ad_added_typical | 17 | packages pip check added in 15 of the 17 environments | AgentDefect/SelfHeal/test_env_logs/list_*_install.json | most common len(added) | 2026-11-13 |
| ad_envs_with_typical_added | 15 | environments where pip check added 17 packages | AgentDefect/SelfHeal/test_env_logs/list_*_install.json | count of len(added) == 17 | 2026-11-13 |
| ad_added_list13 | 111 | packages pip check added for list 13 | AgentDefect/SelfHeal/test_env_logs/list_13_install.json | len(added) | 2026-11-13 |
| ad_list1c_replaced | 11 | pins of list_1c at list 4's versions | AgentDefect/SelfHeal/test_env_logs/list_1c_install.json | len(pins_replaced) | 2026-11-13 |
| ad_tests | 555 | test records of the AgentDefect repairs, one per rerun | AgentDefect/SelfHeal/<model>/<case>/rerun_<k>/test/test_record.json | file count | 2026-11-13 |
| ad_tests_per_case | 15 | tests per case, three models times five reruns | AgentDefect/SelfHeal/code/test_repairs.py | MODELS and RERUNS | 2026-11-13 |
| ad_log_test_repairs_first | 15 | tests run in test_repairs_first.log | AgentDefect/SelfHeal/test_repairs_first.log | lines with passed or failed exit | 2026-11-13 |
| ad_log_test_repairs_run_1 | 99 | tests run in test_repairs_run_1.log | AgentDefect/SelfHeal/test_repairs_run_1.log | lines with passed or failed exit | 2026-11-13 |
| ad_log_test_repairs_run_3 | 90 | tests run in test_repairs_run_3.log | AgentDefect/SelfHeal/test_repairs_run_3.log | lines with passed or failed exit | 2026-11-13 |
| ad_log_test_repairs_run_4 | 120 | tests run in test_repairs_run_4.log | AgentDefect/SelfHeal/test_repairs_run_4.log | lines with passed or failed exit | 2026-11-13 |
| ad_log_test_repairs_run | 405 | tests run in test_repairs_run.log | AgentDefect/SelfHeal/test_repairs_run.log | lines with passed or failed exit | 2026-11-13 |
| ad_log_test_repairs_run_fixes | 105 | tests run in test_repairs_run_fixes.log | AgentDefect/SelfHeal/test_repairs_run_fixes.log | lines with passed or failed exit | 2026-11-13 |
| ad_log_test_repairs_run_1c | 15 | tests run in test_repairs_run_1c.log | AgentDefect/SelfHeal/test_repairs_run_1c.log | lines with passed or failed exit | 2026-11-13 |
| ad_log_test_repairs_run_1c2 | 15 | tests run in test_repairs_run_1c2.log | AgentDefect/SelfHeal/test_repairs_run_1c2.log | lines with passed or failed exit | 2026-11-13 |
| ad_test_runs_total | 864 | test runs over all AgentDefect test logs, deleted ones included | AgentDefect/SelfHeal/test_repairs_*.log | sum of the log rows above | 2026-11-13 |
| ad_subfolder_test_folders | 90 | final test folders of the six cases with subfolder files that hold every such file | /data/wang/junh/githubs/SelfHeal/AgentDefect.zip | case files in subfolders checked in each */<case>/rerun_*/test | 2026-11-13 |
| ad_table_cases | 36 | cases in the AgentDefect success table, 79776520 left out | AgentDefect/SelfHeal/code/score_tests.py | cases minus DROPPED | 2026-11-13 |
| ad_table_reruns | 180 | reruns per model in the AgentDefect success table | AgentDefect/SelfHeal/code/score_tests.py | 36 cases times five | 2026-11-13 |
| pg_port | 5432 | Postgres port the 79497660 test connects to | AgentDefect/SelfHeal/code/test_repairs.py | start_postgres | 2026-11-13 |
| ad_ollama_port | 11434 | port of the local Ollama server | AgentDefect/SelfHeal/code/test_repairs.py | OLLAMA_URL | 2026-11-13 |
| aib_issues | 50 | AgentIssue-Bench issues | AgentIssue-Bench/motivation_experiment/artifacts/agentissue/entrypoints.json | records | 2026-11-13 |
| aib_amd64 | 36 | issues whose published image is built for amd64 | AgentIssue-Bench/motivation_experiment/artifacts/agentissue/entrypoints.json | architecture amd64 | 2026-11-13 |
| aib_rebuilt | 14 | issues rebuilt for amd64 | AgentIssue-Bench/images_amd64 | tag folders | 2026-11-13 |
| aib_tree_image | 34 | issues whose repository files come from the image | AgentIssue-Bench/SelfHeal/inputs/issues/*/record.json | tree_source | 2026-11-13 |
| aib_tree_clone | 16 | issues whose repository files are cloned at the image's buggy commit | AgentIssue-Bench/SelfHeal/inputs/issues/*/record.json | tree_source | 2026-11-13 |
| aib_named | 20 | issues whose report names at least one repository file | AgentIssue-Bench/SelfHeal/inputs/named_files.json | non-empty lists | 2026-11-13 |
| aib_pick | 30 | issues whose files the model picks | AgentIssue-Bench/SelfHeal/inputs/named_files.json | empty lists | 2026-11-13 |
| aib_named_max_chars | 150008 | largest joined size of named files of one issue, in bytes (autogen_3361) | AgentIssue-Bench/SelfHeal/inputs/issues | sum of file sizes | 2026-11-13 |
| aib_reruns_per_model | 250 | planned SelfHeal reruns per model on AgentIssue-Bench | AgentIssue-Bench/SelfHeal/code/driver.py | 50 issues times five | 2026-11-13 |
| aib_reruns_total | 750 | planned reruns and tests on AgentIssue-Bench, three models | AgentIssue-Bench/SelfHeal/code/test_repairs.py | 50 issues times 15 | 2026-11-13 |
| aib_timeout | 300 | seconds the benchmark allows one test | /data/wang/junh/githubs/AgentIssue-Bench/eval_patches.py | timeout=300, line 112 | 2026-11-13 |
| env_selfheal_pins | 73 | distributions installed in the rebuilt selfheal environment | AgentIssue-Bench/SelfHeal/inputs/env_selfheal_pins.txt | line count | 2026-11-13 |
| env_openai028_pins | 24 | distributions in the rebuilt selfheal-openai028 environment | AgentIssue-Bench/SelfHeal/inputs/env_selfheal_openai028_pins.txt | line count | 2026-11-13 |
| http_not_found | 404 | HTTP status GitHub returns for crewAIInc/crewAI issue 1824, page and API | AgentIssue-Bench/motivation_experiment/artifacts/agentissue/issues/crewai_1824.json | status note, checked again with curl | 2026-11-13 |
| check_call_limit | 32768 | length limit I set on an ARC check call, the mistake behind the no length limit rule | /home/grads/junh/.claude/CLAUDE.md | section No token limit on any model call, Why | 2026-11-13 |
| aib_gptoss_picks | 30 | issues with a finished gpt-oss-120b file pick | AgentIssue-Bench/SelfHeal/gpt-oss-120b/*/pick/pick.json | file count | 2026-11-13 |
| aib_corrected | 30 | issues with a corrected evaluator, departures 5 and 13 | AgentIssue-Bench/SelfHeal/evaluator/corrections.json | keys | 2026-11-13 |
| aib_shipped_only | 20 | issues with only the shipped evaluator | AgentIssue-Bench/SelfHeal/evaluator/corrections.json | 50 minus the keys | 2026-11-13 |
| aib_cal_corr_separates | 16 | issues whose corrected evaluator passes the developer patch five of five and the null patch none, gpt-oss-120b | AgentIssue-Bench/case_check/gpt-oss-120b | five runs of each control | 2026-11-13 |
| aib_cal_ship_corr_bothfail | 30 | issues with a corrected evaluator whose shipped evaluator fails both controls five of five, gpt-oss-120b | AgentIssue-Bench/case_check/gpt-oss-120b | five runs of each control | 2026-11-13 |
| aib_cal_ship_bothfail_all | 34 | issues whose shipped evaluator fails both controls, gpt-oss-120b | AgentIssue-Bench/case_check/gpt-oss-120b | five runs of each control | 2026-11-13 |
| aib_cal_separating_final | 22 | issues whose final evaluator tells the developer patch from the null patch, gpt-oss-120b | AgentIssue-Bench/case_check/gpt-oss-120b | corrected evaluator where one exists, else shipped | 2026-11-13 |
| aib_gptoss_accepted | 67 | gpt-oss-120b AgentIssue-Bench kept reruns SelfHeal marked ACCEPTED | AgentIssue-Bench/SelfHeal/gpt-oss-120b/<tag>/rerun_<k>/Fix-Agent/results | Status line | 2026-11-13 |
| aib_initial_adaptation | 21 | gpt-oss-120b reruns of the first adaptation, kept apart | AgentIssue-Bench/SelfHeal/gpt-oss-120b/_initial_adaptation | rerun folders | 2026-11-13 |
| aib_ds_openrouter | 32 | DeepSeek-V4.1-Flash AgentIssue-Bench kept reruns run through OpenRouter | AgentIssue-Bench/SelfHeal/DeepSeek-V4.1-Flash/<tag>/rerun_<k>/run_record.json | provider of the run step | 2026-11-13 |
| aib_gptoss_failed | 182 | gpt-oss-120b AgentIssue-Bench kept reruns SelfHeal marked FAILED | AgentIssue-Bench/SelfHeal/gpt-oss-120b/<tag>/rerun_<k>/Fix-Agent/results | Status line | 2026-11-13 |
| fix_plan_departure_numbers | 11, 12, 13, 14, 15, 16 | numbers of the fix plan departures the report cites above ten | /home/grads/junh/.claude/plans/write-delivery-in-plan-bench-md-calm-clock.md | numbered list under Departures from your instruction | 2026-11-13 |
