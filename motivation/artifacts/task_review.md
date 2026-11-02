# Review of the drafted questions

## 76897509

The published question is kept. No second question was added, because the papers do not state another expected answer in the case files.

What this case can support so far: public_reproducer_only.

- public_reproducer: What is Theia

## 78366661

The published job is to search one outside PDF and return matching passages. The case has no second document, so no extra question was kept.

What this case can support so far: public_reproducer_only.

- public_reproducer: Search https://arxiv.org/pdf/2303.08774.pdf for how much compute GPT-4 training used, and return the matching passages.

## 77178370

The extra questions use the same notes already stored in the program: cars, and the named building materials. They were not chosen after seeing a repair.

What this case can support so far: public_plus_authored_heldout.

- public_reproducer: What are buildings made of?

- related: What are cars made out of?

- related: Which building materials do the notes name?

## 78838421

The published question about love quotes is kept. The paper does not list the quotes, so no extra question with a known answer was added.

What this case can support so far: public_reproducer_only.

- public_reproducer: Give 10 quotes from this articles related to love?

## 79343179

The published program loads excel_file.xlsx into a table. Sentiment and Location are kept because they are columns in that table, including the rows the loader drops, and the expected answer is the exact value of each row in order. Column names and a row count were set aside because they do not check those lost row values.

What this case can support so far: public_plus_authored_heldout.

- public_reproducer: Load the Excel file located at excel_file.xlsx and assign the result to a variable named df.

- related: Read excel_file.xlsx and report the Sentiment value of each row, in order.

- related: Read excel_file.xlsx and report the Location value of each row, in order.

## 77099194

The extra questions ask for every title of another genre in the same spreadsheet. The expected titles are the rows with that genre tag, which is stricter than the published test.

What this case can support so far: public_plus_authored_heldout.

- public_reproducer: Return all the action movies names

- related: Return all the adventure movie names

- related: Return all the animation movie names

## 79149108

Dog and table follow the published yes-or-no animal rule. Horse is the published example and is not treated as already shown to work.

What this case can support so far: public_plus_authored_heldout.

- public_reproducer: We are gonna play a game in which I'm gonna say some words and you have to tell me if the word represents an animal. Just tell me yes or no.

- related: The animal game has already been explained. The word is dog. Answer yes or no.

- related: In the same animal game, the word is table. Answer yes or no.

- regression: In the same animal game, the word is horse. Answer yes or no.

## 78383658

Family, Action, and Adventure titles and descriptions come from the spreadsheet. Name means the title column, and description means the overview column.

What this case can support so far: public_plus_authored_heldout.

- public_reproducer: Find movies for family, combining their Name and Description.

- related: Find movies whose genres include Action. Return each title with its description.

- related: Find movies whose genres include Adventure. Return each title with its description.
