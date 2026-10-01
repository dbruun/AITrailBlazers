# AI Text Summarizer

> Turn long documents, emails and meeting transcripts into short, readable summaries. Works fully
> offline out of the box and switches to Azure OpenAI when configured.

| | |
|---|---|
| **Status** | ready |
| **Audience** | Business stakeholders (walkthrough) · Developers (code + deploy) |
| **Time to demo** | ~5 minutes (walkthrough) · ~10 minutes (deploy) |

## 🖱️ Non-technical: click-through walkthrough

No install required. Open [`walkthrough/index.html`](walkthrough/index.html) in any browser
and use **Next / Back** (or the arrow keys) to step through the story. Press **N** to show
presenter notes.

A written presenter script lives in [`walkthrough/README.md`](walkthrough/README.md).

## 🛠️ Technical: run, deploy and extend

| What | Where |
|---|---|
| Source code | [`src/`](src/) |
| Run locally | [Quickstart](#quickstart) below |
| Deploy to the cloud | [`infra/README.md`](infra/README.md) |
| Extend / customize | [`docs/EXTENDING.md`](docs/EXTENDING.md) |

### Quickstart

```bash
cd demos/text-summarizer/src
python app.py
# open http://127.0.0.1:8000, paste some text and click "Summarize"
```

Or call the API directly:

```bash
curl -s http://127.0.0.1:8000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Paste a few sentences here. ...", "sentences": 2}'
```

Run the tests:

```bash
cd demos/text-summarizer
python -m unittest discover -s tests
```

### Architecture

```
Browser (static/index.html) ──POST /api/summarize──▶ app.py (http.server)
                                                         │
                                                         ▼
                                                   summarizer.py
                                         ┌───────────────┴───────────────┐
                                  offline extractive              Azure OpenAI chat
                                  (default, no deps)        (when AZURE_OPENAI_* env vars set)
```

### Prerequisites

- Python 3.8+ (no third-party packages required)
- Optional: Docker, an Azure subscription and an Azure OpenAI deployment
