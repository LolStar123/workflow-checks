#!/usr/bin/env python3
"""Check local Markdown links in CI-selected documentation files."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"!?\[[^]]*\]\(([^)]+)\)")
EXTERNAL = ("http:", "https:", "//", "mailto:", "data:")


def link_target(raw: str) -> str:
    target = raw.strip().strip("<>")
    # Markdown permits an optional title after a whitespace separator.
    return target.split(maxsplit=1)[0] if target else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths-json", default=None)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository to check")
    args = parser.parse_args()
    root = args.root.resolve()
    failures: list[str] = []
    paths = json.loads(args.paths_json or os.environ.get("TARGETS_JSON", '["README.md"]'))
    for raw_path in paths:
        page = (root / raw_path).resolve()
        try:
            page.relative_to(root)
        except ValueError:
            failures.append(f"outside repository: {raw_path}")
            continue
        if not page.is_file():
            failures.append(f"missing documentation: {raw_path}")
            continue
        if page.suffix.lower() not in {".md", ".mdx", ".rst"} or not page.is_file():
            continue
        for raw_link in MARKDOWN_LINK.findall(page.read_text(encoding="utf-8")):
            target = link_target(raw_link).split("#", 1)[0]
            if not target or target.startswith(EXTERNAL):
                continue
            destination = (page.parent / unquote(target)).resolve()
            try:
                destination.relative_to(root)
            except ValueError:
                failures.append(f"outside repository: {raw_path} -> {raw_link}")
                continue
            if not destination.exists():
                failures.append(f"broken local link: {raw_path} -> {raw_link}")
    if failures:
        raise SystemExit("\n".join(failures))
    print("documentation link check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
