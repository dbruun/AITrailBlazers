# Contributing a demo

Thanks for adding to AITrailBlazers! Every demo must serve **both** audiences: a non-technical
click-through and a technical run/deploy/extend path.

## 1. Scaffold

```bash
python scripts/demos.py new <demo-id> --title "Human Friendly Title"
```

- `<demo-id>` is the folder name and must be lowercase kebab-case (e.g. `invoice-extraction`).
- The title must not contain quotes, `<`, `>`, backslashes or backticks.

## 2. Fill in the pieces

| File | Required content |
|---|---|
| `demo.json` | `id` (matches folder), `title`, `summary`, `status` (`draft` \| `ready` \| `deprecated`), `owners` (GitHub handles), `tags`, `walkthrough`, `deploy.targets`, `deploy.guide`, optional `prerequisites`. |
| `README.md` | Problem statement, links to both tracks, quickstart, architecture, prerequisites. |
| `walkthrough/index.html` | The click-through steps (`window.WALKTHROUGH`). Put screenshots in `walkthrough/assets/`. |
| `walkthrough/README.md` | Presenter script and common Q&A for non-technical presenters. |
| `src/` | Runnable code. Pin dependencies. |
| `infra/README.md` | How to deploy (local + cloud), configuration table, clean-up steps. Keep IaC in `infra/`. |
| `docs/EXTENDING.md` | Extension points and ideas for customizing the demo. |
| `tests/` (optional) | Python demos with `tests/test_*.py` are run automatically in CI. |

### Writing the click-through

Each step in `walkthrough/index.html` supports:

```js
{
  title: "Step title",
  body: "<p>HTML shown to the audience</p>",
  image: "assets/step-1.png",   // optional screenshot
  imageAlt: "Description",      // optional alt text / caption
  notes: "Presenter notes"      // optional, toggled with the N key
}
```

The player (`shared/clickthrough/`) works from `file://`, so presenters can simply double-click
the file. Steps are deep-linkable with `#step-N`.

## 3. Validate

```bash
python scripts/demos.py validate        # structure, metadata, placeholders, catalog
python -m unittest discover -s tests    # repository tooling tests
```

If the catalog is out of date, run `python scripts/demos.py catalog` and commit the result.

## Guidelines

- **Never commit secrets.** Use environment variables and document them in `infra/README.md`.
- Prefer demos that run locally/offline by default and light up cloud services when configured.
- Keep demos self-contained: anything a demo needs should live in its own folder (shared assets
  belong in `shared/`).
- To improve the framework for every demo, update `templates/demo-template/` and `scripts/demos.py`.
