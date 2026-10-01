#!/usr/bin/env python3
"""Tooling for the AITrailBlazers demo catalog.

Usage:
    python scripts/demos.py new <demo-id> --title "Human friendly title"
    python scripts/demos.py validate
    python scripts/demos.py catalog [--check]

Only the Python standard library is used so the tool runs anywhere Python 3.8+ is installed.
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEMOS_DIR_NAME = "demos"
TEMPLATE_DIR = Path("templates") / "demo-template"
CATALOG_FILE_NAME = "README.md"
CATALOG_START = "<!-- CATALOG:START -->"
CATALOG_END = "<!-- CATALOG:END -->"

ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLACEHOLDER_PATTERN = re.compile(r"\{\{DEMO_[A-Z_]+\}\}")
UNSAFE_TITLE_PATTERN = re.compile(r'["<>\\\r\n`]')
VALID_STATUSES = ("draft", "ready", "deprecated")
TEXT_SUFFIXES = {
    ".md", ".json", ".html", ".css", ".js", ".ts", ".py", ".txt", ".yml", ".yaml",
    ".bicep", ".tf", ".sh", ".ps1", ".toml", ".cfg", ".ini", ".env", "",
}

REQUIRED_FILES = (
    "README.md",
    "demo.json",
    "walkthrough/index.html",
    "walkthrough/README.md",
    "infra/README.md",
    "docs/EXTENDING.md",
)
REQUIRED_DIRS = ("src",)


def demos_dir(root):
    return Path(root) / DEMOS_DIR_NAME


def list_demo_dirs(root):
    base = demos_dir(root)
    if not base.is_dir():
        return []
    return sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith("."))


def load_metadata(demo_dir):
    with open(demo_dir / "demo.json", encoding="utf-8") as handle:
        return json.load(handle)


def _is_str_list(value, allow_empty=True):
    return (
        isinstance(value, list)
        and all(isinstance(v, str) and v.strip() for v in value)
        and (allow_empty or len(value) > 0)
    )


def validate_metadata(meta, demo_dir):
    """Return a list of error strings for a parsed demo.json."""
    errors = []
    if not isinstance(meta, dict):
        return ["demo.json must contain a JSON object"]

    for key in ("id", "title", "summary", "status", "walkthrough"):
        if not isinstance(meta.get(key), str) or not meta.get(key).strip():
            errors.append("demo.json: '%s' must be a non-empty string" % key)

    if isinstance(meta.get("id"), str) and meta["id"] != demo_dir.name:
        errors.append(
            "demo.json: 'id' (%s) must match the folder name (%s)" % (meta["id"], demo_dir.name)
        )
    if isinstance(meta.get("status"), str) and meta["status"] not in VALID_STATUSES:
        errors.append(
            "demo.json: 'status' must be one of %s" % ", ".join(VALID_STATUSES)
        )
    if not _is_str_list(meta.get("owners"), allow_empty=False):
        errors.append("demo.json: 'owners' must be a non-empty list of strings")
    if not _is_str_list(meta.get("tags")):
        errors.append("demo.json: 'tags' must be a list of strings")
    if "prerequisites" in meta and not _is_str_list(meta.get("prerequisites")):
        errors.append("demo.json: 'prerequisites' must be a list of strings")

    walkthrough = meta.get("walkthrough")
    if isinstance(walkthrough, str) and walkthrough.strip():
        if not _is_inside(demo_dir, walkthrough) or not (demo_dir / walkthrough).is_file():
            errors.append("demo.json: 'walkthrough' file not found: %s" % walkthrough)

    deploy = meta.get("deploy")
    if not isinstance(deploy, dict):
        errors.append("demo.json: 'deploy' must be an object with 'targets' and 'guide'")
    else:
        if not _is_str_list(deploy.get("targets"), allow_empty=False):
            errors.append("demo.json: 'deploy.targets' must be a non-empty list of strings")
        guide = deploy.get("guide")
        if not isinstance(guide, str) or not guide.strip():
            errors.append("demo.json: 'deploy.guide' must be a non-empty string")
        elif not _is_inside(demo_dir, guide) or not (demo_dir / guide).is_file():
            errors.append("demo.json: 'deploy.guide' file not found: %s" % guide)

    return errors


def _is_inside(base, relative):
    try:
        (base / relative).resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def validate_demo(demo_dir):
    """Return a list of error strings for a single demo folder."""
    demo_dir = Path(demo_dir)
    errors = []

    if not ID_PATTERN.match(demo_dir.name):
        errors.append("folder name must be lowercase kebab-case (e.g. 'my-demo')")

    for rel in REQUIRED_FILES:
        if not (demo_dir / rel).is_file():
            errors.append("missing required file: %s" % rel)
    for rel in REQUIRED_DIRS:
        path = demo_dir / rel
        if not path.is_dir():
            errors.append("missing required folder: %s/" % rel)
        elif not any(p.is_file() for p in path.rglob("*")):
            errors.append("folder must contain at least one file: %s/" % rel)

    if (demo_dir / "demo.json").is_file():
        try:
            meta = load_metadata(demo_dir)
        except (ValueError, OSError) as exc:
            errors.append("demo.json is not valid JSON: %s" % exc)
        else:
            errors.extend(validate_metadata(meta, demo_dir))

    for path in sorted(demo_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if PLACEHOLDER_PATTERN.search(text):
                errors.append(
                    "unreplaced template placeholder in %s" % path.relative_to(demo_dir).as_posix()
                )

    return errors


def render_catalog(root):
    rows = [
        "| Demo | Summary | Status | Tags | Walkthrough | Deploy |",
        "|---|---|---|---|---|---|",
    ]
    for demo_dir in list_demo_dirs(root):
        try:
            meta = load_metadata(demo_dir)
        except (ValueError, OSError):
            continue
        if validate_metadata(meta, demo_dir):
            continue
        name = demo_dir.name
        tags = ", ".join("`%s`" % t for t in meta.get("tags", []))
        deploy = meta.get("deploy", {}) or {}
        targets = ", ".join(deploy.get("targets", []))
        rows.append(
            "| [%s](%s/) | %s | %s | %s | [Click-through](%s/%s) | [%s](%s/%s) |"
            % (
                _md_cell(meta.get("title", name)),
                name,
                _md_cell(meta.get("summary", "")),
                _md_cell(meta.get("status", "")),
                tags,
                name,
                meta.get("walkthrough", ""),
                _md_cell(targets or "guide"),
                name,
                deploy.get("guide", ""),
            )
        )
    if len(rows) == 2:
        rows.append("| _No demos yet_ | | | | | |")
    return "\n".join(rows)


def _md_cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def update_catalog(root, check=False):
    """Regenerate the catalog table. Returns True if the file is (now) up to date."""
    path = demos_dir(root) / CATALOG_FILE_NAME
    content = path.read_text(encoding="utf-8")
    start = content.find(CATALOG_START)
    end = content.find(CATALOG_END)
    if start == -1 or end == -1 or end < start:
        raise ValueError(
            "%s must contain %s and %s markers" % (path, CATALOG_START, CATALOG_END)
        )
    new_content = (
        content[: start + len(CATALOG_START)]
        + "\n"
        + render_catalog(root)
        + "\n"
        + content[end:]
    )
    if new_content == content:
        return True
    if check:
        return False
    path.write_text(new_content, encoding="utf-8")
    return True


def create_demo(root, demo_id, title):
    """Copy the template into demos/<demo_id> and fill in placeholders."""
    root = Path(root)
    if not ID_PATTERN.match(demo_id):
        raise ValueError("demo id must be lowercase kebab-case, e.g. 'invoice-extraction'")
    if not title.strip() or UNSAFE_TITLE_PATTERN.search(title):
        raise ValueError("title must be non-empty and must not contain quotes, <, >, \\, backticks or newlines")
    target = demos_dir(root) / demo_id
    if target.exists():
        raise ValueError("demo already exists: %s" % target)

    shutil.copytree(root / TEMPLATE_DIR, target)
    replacements = {"{{DEMO_ID}}": demo_id, "{{DEMO_TITLE}}": title}
    for path in target.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8")
            for old, new in replacements.items():
                text = text.replace(old, new)
            path.write_text(text, encoding="utf-8")
    update_catalog(root)
    return target


def cmd_new(args):
    title = args.title or args.id.replace("-", " ").title()
    try:
        target = create_demo(args.root, args.id, title)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    print("Created %s" % target)
    print("Next steps:")
    print("  1. Fill in demo.json, README.md and the walkthrough steps.")
    print("  2. Add your code to src/ and deployment assets to infra/.")
    print("  3. Run: python scripts/demos.py validate")
    return 0


def cmd_validate(args):
    root = Path(args.root)
    failed = False
    demo_dirs = list_demo_dirs(root)
    for demo_dir in demo_dirs:
        errors = validate_demo(demo_dir)
        if errors:
            failed = True
            print("FAIL %s" % demo_dir.name)
            for err in errors:
                print("  - %s" % err)
        else:
            print("ok   %s" % demo_dir.name)
    try:
        if not update_catalog(root, check=True):
            failed = True
            print("FAIL catalog: demos/README.md is out of date. Run: python scripts/demos.py catalog")
    except (ValueError, OSError) as exc:
        failed = True
        print("FAIL catalog: %s" % exc)
    print("%d demo(s) checked" % len(demo_dirs))
    return 1 if failed else 0


def cmd_catalog(args):
    try:
        ok = update_catalog(args.root, check=args.check)
    except (ValueError, OSError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    if args.check:
        print("catalog is up to date" if ok else "catalog is out of date")
        return 0 if ok else 1
    print("catalog updated")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="Manage AITrailBlazers demos.")
    parser.add_argument("--root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    new = sub.add_parser("new", help="scaffold a new demo from the template")
    new.add_argument("id", help="lowercase kebab-case folder name, e.g. invoice-extraction")
    new.add_argument("--title", help="human friendly title")
    new.set_defaults(func=cmd_new)

    validate = sub.add_parser("validate", help="validate every demo and the catalog")
    validate.set_defaults(func=cmd_validate)

    catalog = sub.add_parser("catalog", help="regenerate the catalog in demos/README.md")
    catalog.add_argument("--check", action="store_true", help="fail if the catalog is stale")
    catalog.set_defaults(func=cmd_catalog)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
