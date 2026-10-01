# AITrailBlazers

A home for **reusable AI demos** that anyone can clone, present and extend.

Every demo ships with two tracks:

| Track | Who it's for | What you get |
|---|---|---|
| 🖱️ **Click-through walkthrough** | Non-technical audiences: sellers, executives, business users | A browser-based, step-by-step story (`walkthrough/index.html`) plus a presenter script. No install, no code. |
| 🛠️ **Code, deploy & extend** | Developers, architects, technical sellers | Runnable source (`src/`), deployment guide and IaC (`infra/`), and extension ideas (`docs/EXTENDING.md`). |

👉 **Browse the demos in the [demo catalog](demos/README.md).**

## Quick start

```bash
git clone https://github.com/dbruun/AITrailBlazers.git
cd AITrailBlazers
```

- **Presenting?** Open `demos/<demo>/walkthrough/index.html` in your browser. Use the arrow keys to
  move between steps and **N** to toggle presenter notes.
- **Building?** Follow `demos/<demo>/README.md` to run locally, then `infra/README.md` to deploy.

## Repository layout

```
.
├── demos/                      # One folder per demo (see demos/README.md for the catalog)
│   └── <demo-id>/
│       ├── demo.json           # Metadata: title, summary, status, owners, tags, deploy targets
│       ├── README.md           # Landing page with both tracks + quickstart
│       ├── walkthrough/        # 🖱️ Non-technical click-through
│       │   ├── index.html      #    Steps rendered by the shared click-through player
│       │   ├── README.md       #    Presenter script / talking points
│       │   └── assets/         #    Screenshots used by the walkthrough
│       ├── src/                # 🛠️ Runnable code (any language)
│       ├── infra/              # 🛠️ Deployment guide + IaC (Bicep, Terraform, scripts)
│       ├── docs/EXTENDING.md   # 🛠️ How to customize / extend
│       └── tests/              # Optional automated tests
├── templates/demo-template/    # Starting point for new demos
├── shared/clickthrough/        # Dependency-free click-through player (JS + CSS)
├── scripts/demos.py            # CLI: scaffold, validate and catalog demos
└── tests/                      # Tests for the repository tooling
```

## Adding a new demo

```bash
python scripts/demos.py new my-new-demo --title "My New Demo"   # scaffold from the template
# ...fill in demo.json, walkthrough, src/, infra/, docs/...
python scripts/demos.py validate                               # check structure + catalog
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full checklist.

## Tooling

`scripts/demos.py` only needs Python 3.8+ (standard library only):

| Command | What it does |
|---|---|
| `python scripts/demos.py new <id> --title "..."` | Copies `templates/demo-template` to `demos/<id>`, fills in placeholders, updates the catalog. |
| `python scripts/demos.py validate` | Checks every demo has the required files and valid `demo.json`, and that the catalog is current. |
| `python scripts/demos.py catalog [--check]` | Regenerates (or checks) the catalog table in `demos/README.md`. |

The [Validate demos](.github/workflows/validate-demos.yml) workflow runs validation, the tooling
tests and each demo's tests on every pull request.
