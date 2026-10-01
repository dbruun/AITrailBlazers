# Extending AI Text Summarizer

## Extension points

| Area | File | How to extend |
|---|---|---|
| Summarization logic | [`src/summarizer.py`](../src/summarizer.py) | Add a new `summarize_*` function and select it in `summarize()`. |
| Prompt | `SYSTEM_PROMPT` in `src/summarizer.py` | Change tone, length, language or output format (e.g. bullet points). |
| API | [`src/app.py`](../src/app.py) | Add new routes in `do_GET` / `do_POST`. |
| UI | [`src/static/index.html`](../src/static/index.html) | Rebrand, add file upload, etc. |
| Deployment | [`infra/`](../infra/) | Add Bicep/Terraform alongside the Dockerfile. |

## Ideas

- **Bullet-point action items:** change the prompt to return decisions and owners from meeting notes.
- **Document upload:** accept PDF/Word files and extract text before summarizing.
- **Multi-language:** ask the model to summarize in the reader's language.
- **Managed identity:** replace the API key with Microsoft Entra ID authentication.

## Testing

```bash
python -m unittest discover -s tests
```
