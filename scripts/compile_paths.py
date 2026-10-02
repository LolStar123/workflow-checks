#!/usr/bin/env python3
"""Compile CI-selected Python files without importing their runtime dependencies."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths-json", default=None)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository to check")
    args = parser.parse_args()
    root = args.root.resolve()
    paths = json.loads(args.paths_json or os.environ.get("TARGETS_JSON", "[]"))
    if not paths:
        paths = ["scripts/detect_ci_matrix.py"]

    failures: list[str] = []
    for raw_path in paths:
        candidate = (root / raw_path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            failures.append(f"outside repository: {raw_path}")
            continue
        if not candidate.is_file() or candidate.suffix != ".py":
            failures.append(f"not a Python file: {raw_path}")
            continue
        try:
            compile(candidate.read_text(encoding="utf-8"), str(candidate), "exec", dont_inherit=True)
            print(f"compiled {raw_path}")
        except (OSError, SyntaxError, UnicodeDecodeError) as error:
            failures.append(f"{raw_path}: {error}")
    if failures:
        raise SystemExit("\n".join(failures))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
