# AI Text Summarizer – presenter script

This script accompanies the click-through walkthrough in [`index.html`](index.html).
It is written for a non-technical presenter: no code, no setup.

## Before you start

- Open `index.html` in a browser (double-click the file, or open it from GitHub Pages).
- Press **F11** for full screen. Use the arrow keys to move between steps, **N** for notes.

## Story

| Step | What the audience sees | What to say |
|---|---|---|
| 1 | Too much to read | Knowledge workers spend hours reading long emails, reports and transcripts. |
| 2 | Paste the text | The user pastes any document into a simple web page – no training needed. |
| 3 | Choose the length | Pick how many sentences the summary should have. |
| 4 | Get the summary | In seconds, the key points appear. Nothing else changes in the user's workflow. |
| 5 | Why it matters | Time saved, faster decisions, and it can be extended to action items, translations and more. |

## Common questions

- **Q:** Is our data sent to the internet?  
  **A:** In offline mode, no – everything runs on the machine. With Azure OpenAI, data stays in your
  Azure tenant and is not used to train models.
- **Q:** Can it summarize in other languages or produce bullet points?  
  **A:** Yes – that is a small change to the instructions given to the AI model.
