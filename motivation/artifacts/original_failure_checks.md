# Did the original programs fail?

These checks use each program as it was published. They are not yet runs of the study model, gpt-6-luna. A case is not ready for the repair experiment until that model has been used as well.

## What was run

The building-notes program was asked, "What are buildings made of?" It returned stored notes about cars, atoms, and "building materials." It did not mention brick. The published check looks for brick, so this run fails that check. The program's own model setting is gpt-3.5-turbo.

The action-movie program was asked for the action movies. It answered with only Quantum of Solace. It did not name Avengers or The Dark Knight Rises, which the published check requires. The retrieval setting asks for one document, and that matches this thin answer.

The family-movie program was asked for family films with a name and a description. It named Tangled, which is a family film, and also Avatar and John Carter, which are not tagged as family films. It missed Harry Potter and the Half-Blood Prince, the other family film in the sheet.

## What was checked without calling the model

The PDF-search program's search step returns an empty list for every query. That is the failure. The full entry point was not run, because it would download a long outside paper and embed it, then throw those embeddings away.

The spreadsheet program's loader skips two rows and collapses the sheet. The real sheet has four rows, starting with London and the UK. The loader result starts at the Vagabonds row and does not keep the six columns. The program also contains a tool that can run shell commands, so the full agent was not started.

## OpenAI in place of Ollama

The animal-game and love-quotes programs call Ollama. That program is not installed here. On instruction, those calls were sent to gpt-6-luna, temperature 0, with no extra reasoning. The published files were not edited. The same replacement is applied before either version of a program is imported.

The animal game was given the published conversation. Horse and elephant were answered yes. Car was answered no. The stored history contains the five user turns and no assistant reply. That omission is still present. The yes-or-no answers do not depend on it.

The love-quotes program read its PDF and answered that the paper contains no passages about love, so it could not give 10 quotes. The published check only requires a nonempty string, so that check would pass. The question was not changed.
