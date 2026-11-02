# AgentDefect extension exp-2026-10-22, contribution of persistent component changes

<!-- hand:start -->
The extension justifies keeping only the three loader edits L1, L2 and L3 in 79343179 and dropping the baseline's docstring and inlining edit DV, because each of the three is required when the other two are present, DV is removable, and the developer's own loader, which makes only two of the edits, fails the frozen table check.

It also shows that the 77178370 published fix, which the pilot's single public pass would have kept, is not adequate, and that the chunk overlap change of the 78366661 published fix is removable. In 78383658 the evaluator-designed retrieval intervention R makes the original program adequate on all three checks, so by Jun's table a retrieval-only repair is sufficient within this tested scope.

### What changed or confirmed the selected repair

These statements rest on the with and without comparisons and the frozen decision rule only.

**76906469, confirmed.** AB is kept. B is required in the context of A. A in the empty context has an inadequate parent, so it receives no verdict. The two comparisons with B alone are interface dependency diagnostics and support no claim about the agent module as a repair scope.

**79343179, changed.** The selected repair moves from the baseline to L1L2L3. Each loader edit is required in the context of the other two, and DV is removable. With DV counted as an action, L1L2L3 has one module and three actions against the baseline's one module and four, so the scope rule selects a smaller action set within the same module scope. L1L2L3 is inclusion minimal in the evaluated domain. This case ran in loader scope only.

**78366661, confirmed.** The baseline is kept. P1 is required in both evaluated contexts and P2 is removable in the context of P1, so the published fix is not inclusion minimal. N+P1 has no successful evaluated reduction, and P1 without N was not run, so its minimality is unresolved. With N counted as an action, N+P1 has three modules and two actions, and the baseline with one module and one action is selected without a tie. The check is a reproduction endpoint, so passage relevance is not established.

**77178370, changed.** The initial candidate, the published fix, is not adequate. It passed buildings once and cars once in three runs and never passed materials. No configuration is adequate, so no repair is retained.

**77099194, changed.** The initial candidate, attempt 2, is not adequate. The published fix passes action and animation but fails adventure in every run. No repair is retained.

**78383658, changed by the retrieval intervention.** No route of exp-2026-10-22 is adequate. In section 7, original+R passes all three checks in all three runs, and R is required in that context. The combined route, published+R, passed family and action in all three runs and adventure in two, so it is unresolved under the three of three rule, and the prompt and parser bundle in the context of R has no adequate parent to assess. By Jun's table a retrieval-only repair is sufficient within this tested scope, and original+R is selected. R is an evaluator-designed development intervention, so this selection is development evidence and not a discovered repair.

**Environment flips, section 8.** One environment input changed per case, and every configuration ran fresh under both conditions. The retained repairs of 79343179, 78366661 and 78383658 held under the changed condition, and none of their 22 comparisons flipped. L1L2L3 stays required edit by edit under pandas 2.2.3, because the two dropped columns are integer columns and select_dtypes removes them under either pandas version. The 78366661 verdicts are the same under text-embedding-3-small. On the 96 row catalog original+R and published+R both pass every check three times, and R stays required in the empty context. The 76906469 condition is unresolved, because the gpt-4 endpoint returned 404 model deprecated for every request, so its two flipped comparisons are not observations of the program. The fresh E0 rerun of 78383658 also passed published+R three times on adventure, where section 7 recorded two of three, so the bundle in the context of R is removable under E0 here and was not assessed there.

**Verdicts with intervals, section 9.** Every comparison row of sections 3, 7 and 8 was re-read with its pass probabilities carrying Jeffreys intervals and its with side runs marked as enacted or not from the trace. All 22 required verdicts hold under the posterior rule, and 17 of them rest on three runs a side, where Fisher's exact test gives 0.10, so the exact test accepts only the five 78383658 rows with nine runs a side. None of the eight removable verdicts holds at the margin 0.2, because three passes against three passes leave a 0.72 probability that the two rates lie within it. The 77178370 published repair passed six of nine runs while two of nine executed its tool, and B alone enacted nothing in any batch. Eleven rows touch a module without a probe, so their enactment is not observable.

### What the traces explained

These statements explain outcomes. No selection above rests on them.

**76906469.** A turns the memory value from a string into a list, but the zero shot agent's second request never carries the first question. Under AB the second request carries it. B alone stops at the memory and prompt boundary before any model request.

**79343179.** The published loader keeps the select_dtypes line, which drops UserName and ScreenName. That is why it fails the table check.

**78366661.** P2 changes only the number of embedded chunks, 362 without it and 367 with it.

**77178370.** The published agent called its retrieval tool in none of its nine runs, and no note reached its model requests, so its passing answers came from the model's own knowledge rather than from the notes. P_core passed materials in exactly the two runs where it called the tool. The audit variant asks the right question, but its retriever returns the top four notes, which leave out stone.

**77099194.** In repetition 1 of the adventure input both missing titles were in the retrieved context, so retrieval coverage does not explain that omission.

**78383658.** In exp-2026-10-22 the expected titles were absent from the retrieved documents in every configuration and input pair, and every evaluated candidate kept the default retrieval limit. In section 7 every R run retrieved all 12 indexed chunks and carried every catalog title in its final model request. With that coverage original+R named every expected title in every run, which supports retrieval coverage as the explanation for the original program's failures. published+R added Tangled to one adventure answer, so coverage does not explain that error.

### Predictions written before the runs

| case | comparison | prediction | observed |
|---|---|---|---|
| 76906469 | A in {} | both fail, memory type str to list, no turn 1 question in the turn 2 request | held |
| 76906469 | B in {A} | required, turn 2 request carries turn 1 | held |
| 76906469 | B diagnostics | stop at memory and prompt, no request | held |
| 79343179 | L1, L2 | required | held |
| 79343179 | L3 | removable when every column is object dtype | contradicted, L3 is required because select_dtypes drops UserName and ScreenName |
| 79343179 | DV | removable | held |
| 78366661 | N | neither side recovers | held |
| 78366661 | P1 | required | held |
| 78366661 | P2 | removable, only the chunk count changes | held, the embedded count changed from 362 to 367 |
| 77178370 | E1 | public not 3/3 | held, stone is not retrieved |
| 77178370 | P_core | adequate, recovery through the tool | not held, unresolved, and its buildings pass came without any tool call |
| 77178370 | P_sys | removable | not assessed, the parent is not adequate |
| 77099194 | K | published adequate | not held, adventure fails with the missing titles in context |
| 77099194 | W1, W2 | inadequate on related questions | held |
| 78383658 | U1, U2 | not adequate, retrieved documents unchanged between sides | held |

<!-- hand:end -->

## 1. Case flow, scopes and qualification

The live stage recorded 174 runs against 174 scheduled, with no retry. Of these, 144 were in model-enabled scopes and 30 were loader episodes.

| status | runs |
|---|---|
| behavioral_failure | 121 |
| completed_pass | 50 |
| interface_runtime_failure | 3 |

| unit | count |
|---|---|
| independent programs run | 6 |
| programs kept as controls without runs | 3 |
| inputs, over all programs | 12 |
| configurations | 32 |
| comparisons | 32 |
| repetitions per configuration and input | 3 |

| case | scope | role here | required checks |
|---|---|---|---|
| 76906469 | full_program | runs | turn2_france qualified |
| 79343179 | loader_only | runs | loader_table qualified, loader_sentiment qualified, loader_location qualified |
| 78366661 | full_program | runs | nonempty_result qualified |
| 77178370 | full_program | runs | buildings qualified, cars qualified, materials qualified |
| 77099194 | full_program | runs | action qualified, adventure qualified, animation qualified |
| 78383658 | full_program | runs | family qualified, action qualified, adventure qualified |
| 76897509 | not run | failure not reproduced in the pilot | Under gpt-6-luna the program answered from the papers. The question was not changed. |
| 78838421 | not run | failure not reproduced in the pilot | Under the OpenAI adaptation the program returned a nonempty answer and the crash did not return. The question was not changed. |
| 79149108 | not run | failure not reproduced in the pilot | Horse, elephant, and car were answered correctly. The missing assistant history did not change those answers, so no repair was started from a failure that was not observed. |

No case has a frozen preservation check, so preservation coverage is absent in every case.

## 2. Existing complete routes against the frozen checks

Each cell gives the outcome over three repetitions and the number of passing repetitions.

### 76906469, new table, gpt-6-luna, the published two-turn conversation

| configuration | origin | turn2_france | adequacy |
|---|---|---|---|
| original | published buggy program | fail 0/3 | inadequate |
| A | constructed from declared actions | fail 0/3 | inadequate |
| B | constructed from declared actions | fail 0/3 | inadequate |
| AB | constructed from declared actions | pass 3/3 | adequate |

### 76906469, historical table from commit cb39baa, gpt-6-luna, 12 task groups with 20 repeats

| arm | episodes | successes |
|---|---|---|
| empty | 240 | 0 |
| A | 240 | 0 |
| B | 240 | 0 |
| AB | 240 | 240 |

### 79343179, scope loader_only

| configuration | origin | loader_table | loader_sentiment | loader_location | adequacy |
|---|---|---|---|---|---|
| original | published buggy program | fail 0/3 | fail 0/3 | fail 0/3 | inadequate |
| baseline | baseline repair | pass 3/3 | pass 3/3 | pass 3/3 | adequate |
| published | published fix, privileged reference | fail 0/3 | pass 3/3 | pass 3/3 | inadequate |

### 78366661

| configuration | origin | nonempty_result | adequacy |
|---|---|---|---|
| original | published buggy program | fail 0/3 | inadequate |
| baseline | baseline repair | pass 3/3 | adequate |
| published | published fix, privileged reference | pass 3/3 | adequate |

### 77178370

| configuration | origin | buildings | cars | materials | adequacy |
|---|---|---|---|---|---|
| original | published buggy program | fail 0/3 | pass 3/3 | fail 0/3 | inadequate |
| audit_E1 | evaluator audit | fail 0/3 | pass 3/3 | pass 3/3 | inadequate |
| published | published fix, privileged reference | unstable 1/3 | unstable 1/3 | fail 0/3 | inadequate |

### 77099194

| configuration | origin | action | adventure | animation | adequacy |
|---|---|---|---|---|---|
| original | published buggy program | fail 0/3 | fail 0/3 | pass 3/3 | inadequate |
| attempt_1 | baseline attempt 1 | fail 0/3 | fail 0/3 | fail 0/3 | inadequate |
| attempt_2 | baseline attempt 2, locked | pass 3/3 | fail 0/3 | fail 0/3 | inadequate |
| published | published fix, privileged reference | pass 3/3 | fail 0/3 | pass 3/3 | inadequate |

### 78383658

| configuration | origin | family | action | adventure | adequacy |
|---|---|---|---|---|---|
| original | published buggy program | fail 0/3 | fail 0/3 | fail 0/3 | inadequate |
| published | published fix, privileged reference | fail 0/3 | fail 0/3 | fail 0/3 | inadequate |

### Leaked variants, audit only, pilot results of 2026-10-20

| case | variant | why excluded | pilot public | pilot related |
|---|---|---|---|---|
| 77178370 | baseline | the repair prompt named brick, wood and stone | 3/3 | cars 3/3, materials 3/3 |
| 78383658 | attempt_1 | the repair prompt named Harry Potter | failed its one public run | not run |
| 78383658 | attempt_2 | built from attempt_1's code | 3/3 | action 0/3, adventure 0/3 |

## 3. With and without comparisons

| comparison | change | components | without | with | class | verdict |
|---|---|---|---|---|---|---|
| 76906469:A|empty | A | memory_representation | original inadequate | A inadequate | admissible | not_assessed_parent_not_adequate |
| 76906469:B|A | B | agent_control | A inadequate | AB adequate | admissible | required_in_context |
| 76906469:A|B | A | memory_representation | B inadequate | AB adequate | interface_dependency_diagnostic | none, diagnostic |
| 76906469:B|empty | B | agent_control | original inadequate | B inadequate | interface_dependency_diagnostic | none, diagnostic |
| 79343179:L1|empty | L1 | loader | original inadequate | L1 inadequate | admissible | not_assessed_parent_not_adequate |
| 79343179:L1|L2 | L1 | loader | L2 inadequate | L1L2 inadequate | admissible | not_assessed_parent_not_adequate |
| 79343179:L1|L3 | L1 | loader | L3 inadequate | L1L3 inadequate | admissible | not_assessed_parent_not_adequate |
| 79343179:L1|L2+L3 | L1 | loader | L2L3 inadequate | L1L2L3 adequate | admissible | required_in_context |
| 79343179:L2|empty | L2 | loader | original inadequate | L2 inadequate | admissible | not_assessed_parent_not_adequate |
| 79343179:L2|L1 | L2 | loader | L1 inadequate | L1L2 inadequate | admissible | not_assessed_parent_not_adequate |
| 79343179:L2|L3 | L2 | loader | L3 inadequate | L2L3 inadequate | admissible | not_assessed_parent_not_adequate |
| 79343179:L2|L1+L3 | L2 | loader | L1L3 inadequate | L1L2L3 adequate | admissible | required_in_context |
| 79343179:L3|empty | L3 | loader | original inadequate | L3 inadequate | admissible | not_assessed_parent_not_adequate |
| 79343179:L3|L1 | L3 | loader | L1 inadequate | L1L3 inadequate | admissible | not_assessed_parent_not_adequate |
| 79343179:L3|L2 | L3 | loader | L2 inadequate | L2L3 inadequate | admissible | not_assessed_parent_not_adequate |
| 79343179:L3|L1+L2 | L3 | loader | L1L2 inadequate | L1L2L3 adequate | admissible | required_in_context |
| 79343179:DV|L1+L2+L3 | DV | loader | L1L2L3 adequate | baseline adequate | admissible | removable_in_context |
| 78366661:N|empty | N | execution_control, document_splitting | original inadequate | N inadequate | admissible | not_assessed_parent_not_adequate |
| 78366661:P1|N | P1 | vector_store | N inadequate | N+P1 adequate | admissible | required_in_context |
| 78366661:P1|N+P2 | P1 | vector_store | N+P2 inadequate | published adequate | admissible | required_in_context |
| 78366661:P2|N | P2 | document_splitting | N inadequate | N+P2 inadequate | admissible | not_assessed_parent_not_adequate |
| 78366661:P2|N+P1 | P2 | document_splitting | N+P1 adequate | published adequate | admissible | removable_in_context |
| 77178370:E1|empty | E1 | execution_control | original inadequate | audit_E1 inadequate | admissible | not_assessed_parent_not_adequate |
| 77178370:P_core|empty | P_core | prompt, memory, chain_control, execution_control, tools | original inadequate | P_core unresolved | admissible | not_assessed_parent_not_adequate |
| 77178370:P_sys|P_core | P_sys | prompt | P_core unresolved | published inadequate | admissible | not_assessed_parent_not_adequate |
| 77099194:K|empty | K | retrieval | original inadequate | published inadequate | admissible | not_assessed_parent_not_adequate |
| 77099194:W1|empty | W1 | model_client, data_loading, retrieval, chain_control | original inadequate | attempt_1 inadequate | admissible | not_assessed_parent_not_adequate |
| 77099194:W2|empty | W2 | model_client, data_loading, retrieval, chain_control | original inadequate | attempt_2 inadequate | admissible | not_assessed_parent_not_adequate |
| 78383658:U1|empty | U1 | output_parsing, prompt, chain_control | original inadequate | U1 inadequate | admissible | not_assessed_parent_not_adequate |
| 78383658:U1|U2 | U1 | output_parsing, prompt, chain_control | U2 inadequate | published inadequate | admissible | not_assessed_parent_not_adequate |
| 78383658:U2|empty | U2 | prompt | original inadequate | U2 inadequate | admissible | not_assessed_parent_not_adequate |
| 78383658:U2|U1 | U2 | prompt | U1 inadequate | published inadequate | admissible | not_assessed_parent_not_adequate |

| case | change | useful observed | conditionally necessary observed | redundant within evaluated contexts |
|---|---|---|---|---|
| 76906469 | A | False | False | False |
| 76906469 | B | True | False | False |
| 79343179 | L1 | True | False | False |
| 79343179 | L2 | True | False | False |
| 79343179 | L3 | True | False | False |
| 79343179 | DV | False | False | True |
| 78366661 | N | False | False | False |
| 78366661 | P1 | True | False | False |
| 78366661 | P2 | False | False | True |
| 77178370 | E1 | False | False | False |
| 77178370 | P_core | False | False | False |
| 77178370 | P_sys | False | False | False |
| 77099194 | K | False | False | False |
| 77099194 | W1 | False | False | False |
| 77099194 | W2 | False | False | False |
| 78383658 | U1 | False | False | False |
| 78383658 | U2 | False | False | False |

L1L2L3 is inclusion minimal in the evaluated domain. Every coherent proper subset was run and is inadequate.
baseline is not inclusion minimal, because the evaluated reduction L1L2L3 is adequate.
N+P1 has no successful evaluated reduction. P1 without N was not run, so its minimality is unresolved.
published is not inclusion minimal, because the evaluated reduction N+P1 is adequate.

The 76906469 comparisons that contain B without A are interface dependency diagnostics. B stopped before any model request with the error that chat_history should be a list of base messages. They support no claim about the agent module as a repair scope.

## 4. Intermediate observations, repetition 1 of each input unless stated

### 76906469

| configuration | memory value type | model requests | turn 2 request holds the turn 1 question | stop stage |
|---|---|---|---|---|
| original | str | 2 | no | completed |
| A | list | 2 | no | completed |
| B | str | 0 | no | memory |
| AB | list | 2 | yes | completed |

### 79343179

| configuration | columns | expected names present | names missing | rows |
|---|---|---|---|---|
| original | 1 | 0 | UserName, ScreenName, Location, TweetAt, OriginalTweet, Sentiment | 2 |
| L1 | 1 | 0 | UserName, ScreenName, Location, TweetAt, OriginalTweet, Sentiment | 4 |
| L2 | 4 | 0 | UserName, ScreenName, Location, TweetAt, OriginalTweet, Sentiment | 2 |
| L3 | 1 | 0 | UserName, ScreenName, Location, TweetAt, OriginalTweet, Sentiment | 2 |
| L1L2 | 4 | 4 | UserName, ScreenName | 4 |
| L1L3 | 1 | 0 | UserName, ScreenName, Location, TweetAt, OriginalTweet, Sentiment | 4 |
| L2L3 | 6 | 0 | UserName, ScreenName, Location, TweetAt, OriginalTweet, Sentiment | 2 |
| L1L2L3 | 6 | 6 | none | 4 |
| baseline | 6 | 6 | none | 4 |
| published | 4 | 4 | UserName, ScreenName | 4 |

### 78366661

| configuration | texts embedded | passages returned |
|---|---|---|
| original | 0 | 0 |
| baseline | 0 | 4 |
| N | 0 | 0 |
| N+P1 | 362 | 4 |
| N+P2 | 0 | 0 |
| published | 367 | 4 |

### 77178370, all three repetitions

| configuration | input | runs with a tool call | runs that retrieved notes | runs whose model request held a note | passes |
|---|---|---|---|---|---|
| original | buildings | 0/3 | 3/3 | 3/3 | 0/3 |
| original | cars | 0/3 | 3/3 | 3/3 | 3/3 |
| original | materials | 0/3 | 3/3 | 3/3 | 0/3 |
| audit_E1 | buildings | 0/3 | 3/3 | 3/3 | 0/3 |
| audit_E1 | cars | 0/3 | 3/3 | 3/3 | 3/3 |
| audit_E1 | materials | 0/3 | 3/3 | 3/3 | 3/3 |
| P_core | buildings | 0/3 | 0/3 | 0/3 | 1/3 |
| P_core | cars | 0/3 | 0/3 | 0/3 | 3/3 |
| P_core | materials | 2/3 | 2/3 | 2/3 | 2/3 |
| published | buildings | 0/3 | 0/3 | 0/3 | 1/3 |
| published | cars | 0/3 | 0/3 | 0/3 | 1/3 |
| published | materials | 0/3 | 0/3 | 0/3 | 0/3 |

### 77099194

| configuration | input | documents retrieved | missing titles | missing titles that were in the retrieved context |
|---|---|---|---|---|
| original | action | 1 | 9 | 0 |
| original | adventure | 1 | 9 | 0 |
| original | animation | 1 | 0 | 0 |
| attempt_1 | action | 0 | 10 | 0 |
| attempt_1 | adventure | 0 | 10 | 0 |
| attempt_1 | animation | 0 | 1 | 0 |
| attempt_2 | action | 0 | 0 | 0 |
| attempt_2 | adventure | 0 | 1 | 0 |
| attempt_2 | animation | 0 | 1 | 0 |
| published | action | 12 | 0 | 0 |
| published | adventure | 12 | 2 | 2 |
| published | animation | 12 | 0 | 0 |

### 78383658

| configuration | input | documents retrieved | missing titles | missing titles that were in the retrieved context |
|---|---|---|---|---|
| original | family | 4 | 1 | 0 |
| original | action | 4 | 6 | 0 |
| original | adventure | 4 | 6 | 0 |
| U1 | family | 4 | 1 | 0 |
| U1 | action | 4 | 6 | 0 |
| U1 | adventure | 4 | 6 | 0 |
| U2 | family | 4 | 1 | 0 |
| U2 | action | 4 | 6 | 0 |
| U2 | adventure | 4 | 6 | 0 |
| published | family | 4 | 1 | 0 |
| published | action | 4 | 6 | 0 |
| published | adventure | 4 | 6 | 0 |

## 5. Repair decisions

| case | initial candidate | adequacy before | decision | retained | adequacy after | modules before, after | actions before, after |
|---|---|---|---|---|---|---|---|
| 76906469 | AB | adequate | retained | AB | adequate | 2, 2 | 2, 2 |
| 79343179 | baseline | adequate | retained | L1L2L3 | adequate | 1, 1 | 4, 3 |
| 78366661 | baseline | adequate | retained | baseline | adequate | 1, 1 | 1, 1 |
| 77178370 | published | inadequate | no_adequate_candidate | none | none | 5, none | 2, none |
| 77099194 | attempt_2 | inadequate | no_adequate_candidate | none | none | 4, none | 1, none |
| 78383658 | none | none | no_adequate_candidate | none | none | none, none | none, none |

## 6. Executions, model calls and tokens

Chat model requests numbered 127, and probed runs recorded 299 model API network attempts including embeddings. Chat use was 68673 input and 9326 output tokens. Embedding calls received 2250636 characters. At the pilot price constants and an assumed embedding price the recorded use costs about $0.07.

The 76906469 historical table is read from commit cb39baa and the leaked variants from the pilot results of 2026-10-20. No earlier run was reused as a matched run.

## 7. Retrieval intervention for 78383658, exp-2026-10-22-r

R makes the retriever return every indexed document, with the count read from the index. It is an evaluator-designed development intervention motivated by the traces of section 4, not a discovered repair. All four configurations ran fresh, 36 runs against 36 scheduled, with no retry. The index held 12 chunks.

| configuration | family | action | adventure | adequacy |
|---|---|---|---|---|
| original | fail 0/3 | fail 0/3 | fail 0/3 | inadequate |
| original+R | pass 3/3 | pass 3/3 | pass 3/3 | adequate |
| published | fail 0/3 | fail 0/3 | fail 0/3 | inadequate |
| published+R | pass 3/3 | pass 3/3 | unstable 2/3 | unresolved |

Coverage was verified in 18 of 18 R runs.

| comparison | without | with | class | verdict |
|---|---|---|---|---|
| 78383658:R|empty | original inadequate | original+R adequate | admissible | required_in_context |
| 78383658:R|U1+U2 | published inadequate | published+R unresolved | admissible | not_assessed_parent_not_adequate |
| 78383658:bundle|R | original+R adequate | published+R unresolved | admissible | not_assessed_parent_not_adequate |
| 78383658:bundle|empty | original inadequate | published inadequate | admissible | not_assessed_parent_not_adequate |

| outcome | value |
|---|---|
| supported decision, from Jun's table | A retrieval-only repair is sufficient within this tested scope. |
| selected configuration | original+R |

Chat use was 52416 input and 10550 output tokens.

## 8. Environment flip experiment, exp-2026-10-23-e

One environment input changed per case. Every configuration of the matched comparisons ran fresh under the recorded condition E0 and under the changed condition E1, 192 runs against 192 scheduled, 96 under E0 and 96 under E1, with no retry. A comparison flips when its verdict under E1 differs from its verdict under E0.

| case | E1 change | retained under E0 | retained under E1 | E1 state | flipped comparisons |
|---|---|---|---|---|---|
| 76906469 | chat model gpt-4 in place of gpt-6-luna | AB | none | unresolved, endpoint error | 2 |
| 79343179 | pandas 2.2.3 interpreter in place of pandas 3.0.6 | L1L2L3 | L1L2L3 | observed | 0 |
| 78366661 | embedding model text-embedding-3-small in place of the ada-002 default | baseline | baseline | observed | 0 |
| 78383658 | control.csv with 96 rows in place of 12 | original+R | original+R | observed | 0 |

Flipped comparisons numbered 2 of 26. Of these, 2 sit in a case whose E1 endpoint returned an error for every request, so that environment is unresolved and the difference is not an observation of the program.

### 76906469, chat model gpt-4 in place of gpt-6-luna

| configuration | adequacy under E0 | adequacy under E1 |
|---|---|---|
| original | inadequate (turn2_france fail) | unresolved (turn2_france unresolved) |
| A | inadequate (turn2_france fail) | unresolved (turn2_france unresolved) |
| B | inadequate (turn2_france fail) | unresolved (turn2_france fail) |
| AB | adequate (turn2_france pass) | unresolved (turn2_france unresolved) |

| comparison | verdict under E0 | verdict under E1 | flipped |
|---|---|---|---|
| 76906469:A|empty | not_assessed_parent_not_adequate | inadmissible_unqualified_required_check | yes |
| 76906469:B|A | required_in_context | inadmissible_unqualified_required_check | yes |
| 76906469:A|B | interface_dependency_diagnostic | interface_dependency_diagnostic | no |
| 76906469:B|empty | interface_dependency_diagnostic | interface_dependency_diagnostic | no |

E1 runs not completed, 9. First, endpoint_error NotFoundError Error code: 404 - {'error': {'message': 'The model `gpt-4` has been deprecated, learn more here: https://platform.openai.com/docs/deprecations', 'type': 'invalid_request_error', 'param': None, 'code': 'model_not_found'}}.

### 79343179, pandas 2.2.3 interpreter in place of pandas 3.0.6

| configuration | adequacy under E0 | adequacy under E1 |
|---|---|---|
| original | inadequate (loader_table fail, loader_sentiment fail, loader_location fail) | inadequate (loader_table fail, loader_sentiment fail, loader_location fail) |
| L1 | inadequate (loader_table fail, loader_sentiment fail, loader_location fail) | inadequate (loader_table fail, loader_sentiment fail, loader_location fail) |
| L2 | inadequate (loader_table fail, loader_sentiment fail, loader_location fail) | inadequate (loader_table fail, loader_sentiment fail, loader_location fail) |
| L3 | inadequate (loader_table fail, loader_sentiment fail, loader_location fail) | inadequate (loader_table fail, loader_sentiment fail, loader_location fail) |
| L1L2 | inadequate (loader_table fail, loader_sentiment pass, loader_location pass) | inadequate (loader_table fail, loader_sentiment pass, loader_location pass) |
| L1L3 | inadequate (loader_table fail, loader_sentiment fail, loader_location fail) | inadequate (loader_table fail, loader_sentiment fail, loader_location fail) |
| L2L3 | inadequate (loader_table fail, loader_sentiment fail, loader_location fail) | inadequate (loader_table fail, loader_sentiment fail, loader_location fail) |
| L1L2L3 | adequate (loader_table pass, loader_sentiment pass, loader_location pass) | adequate (loader_table pass, loader_sentiment pass, loader_location pass) |
| baseline | adequate (loader_table pass, loader_sentiment pass, loader_location pass) | adequate (loader_table pass, loader_sentiment pass, loader_location pass) |
| published | inadequate (loader_table fail, loader_sentiment pass, loader_location pass) | inadequate (loader_table fail, loader_sentiment pass, loader_location pass) |

| comparison | verdict under E0 | verdict under E1 | flipped |
|---|---|---|---|
| 79343179:L1|empty | not_assessed_parent_not_adequate | not_assessed_parent_not_adequate | no |
| 79343179:L1|L2 | not_assessed_parent_not_adequate | not_assessed_parent_not_adequate | no |
| 79343179:L1|L3 | not_assessed_parent_not_adequate | not_assessed_parent_not_adequate | no |
| 79343179:L1|L2+L3 | required_in_context | required_in_context | no |
| 79343179:L2|empty | not_assessed_parent_not_adequate | not_assessed_parent_not_adequate | no |
| 79343179:L2|L1 | not_assessed_parent_not_adequate | not_assessed_parent_not_adequate | no |
| 79343179:L2|L3 | not_assessed_parent_not_adequate | not_assessed_parent_not_adequate | no |
| 79343179:L2|L1+L3 | required_in_context | required_in_context | no |
| 79343179:L3|empty | not_assessed_parent_not_adequate | not_assessed_parent_not_adequate | no |
| 79343179:L3|L1 | not_assessed_parent_not_adequate | not_assessed_parent_not_adequate | no |
| 79343179:L3|L2 | not_assessed_parent_not_adequate | not_assessed_parent_not_adequate | no |
| 79343179:L3|L1+L2 | required_in_context | required_in_context | no |
| 79343179:DV|L1+L2+L3 | removable_in_context | removable_in_context | no |

### 78366661, embedding model text-embedding-3-small in place of the ada-002 default

| configuration | adequacy under E0 | adequacy under E1 |
|---|---|---|
| original | inadequate (nonempty_result fail) | inadequate (nonempty_result fail) |
| baseline | adequate (nonempty_result pass) | adequate (nonempty_result pass) |
| N | inadequate (nonempty_result fail) | inadequate (nonempty_result fail) |
| N+P1 | adequate (nonempty_result pass) | adequate (nonempty_result pass) |
| N+P2 | inadequate (nonempty_result fail) | inadequate (nonempty_result fail) |
| published | adequate (nonempty_result pass) | adequate (nonempty_result pass) |

| comparison | verdict under E0 | verdict under E1 | flipped |
|---|---|---|---|
| 78366661:N|empty | not_assessed_parent_not_adequate | not_assessed_parent_not_adequate | no |
| 78366661:P1|N | required_in_context | required_in_context | no |
| 78366661:P1|N+P2 | required_in_context | required_in_context | no |
| 78366661:P2|N | not_assessed_parent_not_adequate | not_assessed_parent_not_adequate | no |
| 78366661:P2|N+P1 | removable_in_context | removable_in_context | no |

### 78383658, control.csv with 96 rows in place of 12

| configuration | adequacy under E0 | adequacy under E1 |
|---|---|---|
| original | inadequate (family fail, action fail, adventure fail) | inadequate (family fail, action fail, adventure fail) |
| original+R | adequate (family pass, action pass, adventure pass) | adequate (family pass, action pass, adventure pass) |
| published | inadequate (family fail, action fail, adventure fail) | inadequate (family fail, action fail, adventure fail) |
| published+R | adequate (family pass, action pass, adventure pass) | adequate (family pass, action pass, adventure pass) |

| comparison | verdict under E0 | verdict under E1 | flipped |
|---|---|---|---|
| 78383658:R|empty | required_in_context | required_in_context | no |
| 78383658:R|U1+U2 | required_in_context | required_in_context | no |
| 78383658:bundle|R | removable_in_context | removable_in_context | no |
| 78383658:bundle|empty | not_assessed_parent_not_adequate | not_assessed_parent_not_adequate | no |

| case | predicted outcome | observed |
|---|---|---|
| 76906469 | AB adequate under gpt-4 | AB unresolved; 9 E1 runs not completed, first endpoint_error NotFoundError Error code: 404 - {'error': {'message': 'The model `gpt-4` has been deprecated, learn more here: https://platform.openai.com/docs/deprecations', 'type': 'invalid_request_error', 'param': None, 'code': 'model_not_found'}}; flips 2 (76906469:A|empty, 76906469:B|A) |
| 76906469 | AB inadequate under gpt-4 | AB unresolved; 9 E1 runs not completed, first endpoint_error NotFoundError Error code: 404 - {'error': {'message': 'The model `gpt-4` has been deprecated, learn more here: https://platform.openai.com/docs/deprecations', 'type': 'invalid_request_error', 'param': None, 'code': 'model_not_found'}}; flips 2 (76906469:A|empty, 76906469:B|A) |
| 76906469 | endpoint error under gpt-4 | AB unresolved; 9 E1 runs not completed, first endpoint_error NotFoundError Error code: 404 - {'error': {'message': 'The model `gpt-4` has been deprecated, learn more here: https://platform.openai.com/docs/deprecations', 'type': 'invalid_request_error', 'param': None, 'code': 'model_not_found'}}; flips 2 (76906469:A|empty, 76906469:B|A) |
| 79343179 | no flip under pandas 2.2.3 | L1L2L3 adequate; baseline adequate; flips 0 |
| 79343179 | L3 removable under pandas 2.2.3 | L1L2L3 adequate; baseline adequate; flips 0 |
| 78366661 | verdicts unchanged under text-embedding-3-small | baseline adequate; N+P1 adequate; published adequate; flips 0 |
| 78366661 | N+P1 inadequate under text-embedding-3-small | baseline adequate; N+P1 adequate; published adequate; flips 0 |
| 78383658 | original+R adequate on 96 rows | original+R adequate; published+R adequate; flips 0 |
| 78383658 | original+R inadequate on 96 rows | original+R adequate; published+R adequate; flips 0 |
| 78383658 | published+R adequate on 96 rows | original+R adequate; published+R adequate; flips 0 |

Chat use was 283492 input and 21295 output tokens over both environments, and embedding calls received 5208648 characters. The gpt-4 price is not among the pilot constants, so no dollar figure is given for this experiment.

## 9. Verdicts with enactment rates and intervals, exp-2026-10-23-v

Every comparison row of sections 3, 7 and 8 is re-read without a model call. Each side's passes over its runs give a Jeffreys Beta posterior of the pass probability, the effect is the posterior of the difference Δ between the with side and the without side, and a with side run counts as enacted when every module the change touches has its boundary event in the run's trace. A required verdict survives when P(Δ > 0) is at least 0.95, a removable verdict when P(abs Δ < 0.2) is at least 0.95, and the other verdict values carry no survival label. Rows, 88, 32 from section 3, four from section 7 and 52 from section 8.

| recorded verdict | rows | survives | fails | no label | never enacted | partially enacted | not observable |
|---|---|---|---|---|---|---|---|
| not_admissible | 8 | 0 | 0 | 8 | 4 | 0 | 0 |
| not_assessed_parent_not_adequate | 50 | 0 | 0 | 50 | 0 | 1 | 8 |
| removable_in_context | 8 | 0 | 8 | 0 | 0 | 0 | 3 |
| required_in_context | 22 | 22 | 0 | 0 | 0 | 0 | 0 |

Enactment. 73 rows have an observed enactment rate, four rows never enacted the change in any with side run, and 11 rows touch a module with no probe, document splitting, the model client or data loading, so their enactment is not observable. `77178370:P_core|empty` in exp-2026-10-22 passed six of nine with side runs while two of nine enacted the change.

Repetition. 17 of the 22 required rows rest on three runs a side. For every one of them Fisher's exact two sided p is 0.10 and P(Δ > 0) is 0.996, so the posterior rule accepts what the exact test does not, and 17 required rows have p at or above 0.05. Of the eight removable rows none survive at the margin, since three against three gives 0.72 and nine against nine 0.95 for the probability that the two pass rates lie within 0.2. The stricter margin 0.1 is reported beside it.

### required_in_context, rows grouped by their counts

| with k/n | without k/n | enacted | rows | P(Δ > 0) | Δ interval | P(abs Δ < 0.1) | P(abs Δ < 0.2) | PN | Fisher p | survives | comparisons |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3/3 | 0/3 | 3/3 | 17 | 1.00 | [0.23, 0.99] | 0.01 | 0.02 | 0.86 | 0.100 | yes | 76906469:B|A (exp-2026-10-22), 79343179:L1|L2+L3 (exp-2026-10-22), 79343179:L2|L1+L3 (exp-2026-10-22), 79343179:L3|L1+L2 (exp-2026-10-22), 78366661:P1|N (exp-2026-10-22), 78366661:P1|N+P2 (exp-2026-10-22), 76906469:B|A@E0 (exp-2026-10-23-e), 79343179:L1|L2+L3@E0 (exp-2026-10-23-e), 79343179:L2|L1+L3@E0 (exp-2026-10-23-e), 79343179:L3|L1+L2@E0 (exp-2026-10-23-e), 79343179:L1|L2+L3@E1 (exp-2026-10-23-e), 79343179:L2|L1+L3@E1 (exp-2026-10-23-e), 79343179:L3|L1+L2@E1 (exp-2026-10-23-e), 78366661:P1|N@E0 (exp-2026-10-23-e), 78366661:P1|N+P2@E0 (exp-2026-10-23-e), 78366661:P1|N@E1 (exp-2026-10-23-e), 78366661:P1|N+P2@E1 (exp-2026-10-23-e) |
| 9/9 | 0/9 | 9/9 | 5 | 1.00 | [0.66, 1.00] | 0.00 | 0.00 | 0.95 | 0.000 | yes | 78383658:R|empty (exp-2026-10-22-r), 78383658:R|empty@E0 (exp-2026-10-23-e), 78383658:R|U1+U2@E0 (exp-2026-10-23-e), 78383658:R|empty@E1 (exp-2026-10-23-e), 78383658:R|U1+U2@E1 (exp-2026-10-23-e) |

### removable_in_context, rows grouped by their counts

| with k/n | without k/n | enacted | rows | P(Δ > 0) | Δ interval | P(abs Δ < 0.1) | P(abs Δ < 0.2) | PN | Fisher p | survives | comparisons |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3/3 | 3/3 | 3/3 | 3 | 0.50 | [-0.46, 0.46] | 0.50 | 0.72 | 0.00 | 1.000 | no | 79343179:DV|L1+L2+L3 (exp-2026-10-22), 79343179:DV|L1+L2+L3@E0 (exp-2026-10-23-e), 79343179:DV|L1+L2+L3@E1 (exp-2026-10-23-e) |
| 3/3 | 3/3 | not observable | 3 | 0.50 | [-0.46, 0.46] | 0.50 | 0.72 | 0.00 | 1.000 | no | 78366661:P2|N+P1 (exp-2026-10-22), 78366661:P2|N+P1@E0 (exp-2026-10-23-e), 78366661:P2|N+P1@E1 (exp-2026-10-23-e) |
| 9/9 | 9/9 | 9/9 | 2 | 0.50 | [-0.21, 0.21] | 0.79 | 0.95 | 0.00 | 1.000 | no | 78383658:bundle|R@E0 (exp-2026-10-23-e), 78383658:bundle|R@E1 (exp-2026-10-23-e) |

The rows without a survival label, with their intervals and enactment, are in `exp-2026-10-23-v/reanalysis.jsonl`. The command is `PYTHONPATH=src python -m motivation_pilot.verdict_reanalysis run`, with `--delta 0.1` for the stricter margin.

