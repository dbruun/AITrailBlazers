# Demo catalog

Every folder in this directory is a self-contained demo. Each demo has:

- 🖱️ a **click-through walkthrough** for non-technical audiences (`walkthrough/index.html`), and
- 🛠️ **code, deployment and extension guides** for technical audiences (`src/`, `infra/`, `docs/`).

The table below is generated from each demo's `demo.json`. Do not edit it by hand – run
`python scripts/demos.py catalog` instead.

<!-- CATALOG:START -->
| Demo | Summary | Status | Tags | Walkthrough | Deploy |
|---|---|---|---|---|---|
| [AI Text Summarizer](text-summarizer/) | Turn long documents, emails and transcripts into short summaries. Runs offline or with Azure OpenAI. | ready | `ai`, `summarization`, `azure-openai`, `python` | [Click-through](text-summarizer/walkthrough/index.html) | [local, docker, azure-container-apps](text-summarizer/infra/README.md) |
<!-- CATALOG:END -->

Want to add a demo? See [CONTRIBUTING.md](../CONTRIBUTING.md).
