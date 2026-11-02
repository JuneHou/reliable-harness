# What the checks establish

| Reported evidence | What it establishes | What remains |
|---|---|---|
| Building and movie programs produced incorrect answers | Those failures also occurred under gpt-6-luna | They still support the pilot |
| PDF search always returns an empty list | A retrieval defect visible without an LLM | Confirmed locally. Complete recovery is for a later repair check |
| Spreadsheet loader drops rows and column names | A loading defect from the source and the sheet | Exact lost cells are recorded below. The full agent is not part of this check |
| Ollama is unavailable | The published programs call a local server that is not installed | Both programs were run with their model calls sent to gpt-6-luna. The published files were not edited |
| Extra questions have independently derived answers | A starting point for evaluation | Frozen inputs, expected outputs, and scoring rules are in frozen_oracles.json |

## Spreadsheet loader

The sheet `excel_file.xlsx` has 4 rows and these columns: UserName, ScreenName, Location, TweetAt, OriginalTweet, Sentiment.

| Row | UserName | ScreenName | Location | TweetAt | Sentiment |
|---|---|---|---|---|---|
| 0 | 3799 | 48751 | London | 16-03-2020 | Neutral |
| 1 | 3800 | 48752 | UK | 16-03-2020 | Positive |
| 2 | 3801 | 48753 | Vagabonds | 16-03-2020 | Positive |
| 3 | 3802 | 48754 |  | 16-03-2020 | Positive |

The published loader uses `skiprows=2` and renames the remaining data to one column, `responses`, then keeps only object columns. The result is two cells, both the word Positive. Rows 0 and 1 are gone. The six column names are gone. The tweet text is gone.

The full agent was not started. It includes a tool that can run shell commands.

## PDF search

The published search object is a dummy. For the query "What were the compute requirements for training GPT 4" it returns `[]`. No model call is required to see that. No second repair was added.

## Pilot run

Repair selection used the public check only. Each score below is 3 repetitions. Held-out questions were scored after the patch was locked. Recorded chat cost for this run is under one cent.

| Program | Original | Baseline patch | What that shows |
|---|---|---|---|
| Buildings | 0/3 on the building question. 3/3 on cars, because the program always looks up the car notes | 3/3 on buildings, cars, and the named materials | The patch recovers the building question and still answers the car question |
| Action movies | 0/3 on action and adventure. 3/3 on animation, which is the one title Tangled | 3/3 on action. 0/3 on adventure and animation. Adventure missed Harry Potter and added The Dark Knight Rises | The public repair works. It does not carry over to the other genres |
| Family movies | 0/3 on family, action, and adventure | 3/3 on family. 0/3 on action and adventure, where it still returns the family films | The public repair works by always selecting the family rows |
| Spreadsheet loader | The loader returns 2 rows and drops Location and Sentiment | The loader returns all 4 rows, with London, UK, Vagabonds, and the four sentiment values | The loader repair keeps the rows the original drops. The shell agent was not started |
| PDF search | 0/3, empty list | 3/3, four passages | One repair, three repetitions. It was not split into a second repair |

A smaller buildings change, which only stops the program from ignoring the question, still misses stone. The published action-movie fix also names all ten action titles. The published family-movie fix still misses Harry Potter. Those two published runs are separate from the baseline scores.

## Qualification under gpt-6-luna

Repair writer and program model are both gpt-6-luna, temperature 0, no extra reasoning. Recorded chat cost for the four runs is under one cent. Embedding calls are extra and were not fully itemized.

| Program | Result under gpt-6-luna | Supports the pilot |
|---|---|---|
| Buildings | Still misses brick, wood, and stone, and returns car notes | Yes |
| Action movies | Names only Avengers: Age of Ultron. Nine other action titles are missing | Yes |
| Family movies | Names Tangled, and also Avatar and John Carter. Misses Harry Potter | Yes |
| What is Theia | Answers from the papers. The old don't-know failure did not return. The question was left unchanged | No |
| PDF search | Empty list, no model call | Yes, as a simple defect |
| Spreadsheet loader | Drops the first two rows and the real column names. Full agent not started | Yes, as a simple defect |
| Animal game | Horse, elephant, and car were answered yes, yes, and no. The assistant's own replies are still missing from the stored history | Yes. The missing history remains. These answers do not depend on it |
| Love quotes | Returned a nonempty answer: the paper has no love quotes. The old crash did not return. The question was left unchanged | No |
