# Limitations

The verdicts concern the evaluated configurations and the frozen checks of each case only.
In 78383658 the expected titles were absent from the retrieved documents in every configuration and input pair of exp-2026-10-22, where every evaluated candidate kept the default retrieval limit.
Title checks of 77099194 and 78383658 use scorer v2, a correction made after outcomes were seen and logged in oracle_corrections.json. It changed three check results in exp-2026-10-22, none of which changed a run status, and eight check results in exp-2026-10-22-r, five of which changed a run status.
The 78383658 retrieval intervention of section 7 is evaluator designed and serves as development evidence, not as a discovered repair. It was tested on the three frozen inputs of that case only.
The PDF case check is a reproduction endpoint. A nonempty passage list does not establish passage relevance or complete PDF search recovery.
The 76906469 check is a limited endpoint that looks for the word france in the second answer. Both raw answers are kept in runs.jsonl.
No case has a frozen preservation check, so no regression claim is made.
79343179 ran in loader scope only. The full agent was not run.
Three repetitions are an observed pass rule for this pilot, not a statement about general reliability.
The 77178370 public check uses the versioned oracle correction of oracle_corrections.json.
The boundary states written during the live run counted installed probes as observations. The tables here recompute them from the traces.
The environment experiment of section 8 changed one input per case and tested each case on its frozen inputs only. A verdict that held under E1 holds for that one changed value and not for the environment in general. The E1 condition of 76906469 is unresolved, because the endpoint returned an error for every request, so no verdict under that condition is an observation of the program.
The reanalysis of section 9 reads the recorded runs only. Its posteriors use the Jeffreys prior on each side, which accepts a three against zero contrast at 0.996 where Fisher's exact test gives 0.10, and both are reported. Enactment is read from the boundary events of the traces, so edits in modules without a probe have no enactment rate.
