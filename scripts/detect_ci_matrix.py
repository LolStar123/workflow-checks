#!/usr/bin/env python3
"""Create the small, path-aware CI matrix used by ``dynamic-ci.yml``.

The script deliberately treats unrecognised changes as baseline work.  A new
directory must not silently opt out of CI while this repository evolves.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Iterable


ALLFLAME_PREFIX = "poe/allflame/"
LEDGER_PREFIXES = ("poe/poe-ledger/", "poe/faustus_flips/")
DOC_SUFFIXES = (".md", ".mdx", ".rst")


def normalise_path(path: str) -> str:
    """Return a repository-relative POSIX path without a leading ``./``."""

    normalised = path.replace("\\", "/")
    while normalised.startswith("./"):
        normalised = normalised[2:]
    return normalised


def is_documentation(path: str) -> bool:
    return path.startswith("docs/") or path.lower().endswith(DOC_SUFFIXES)


def is_known_path(path: str) -> bool:
    return (
        path.startswith(ALLFLAME_PREFIX)
        or path.startswith(LEDGER_PREFIXES)
        or path.endswith(".py")
        or is_documentation(path)
    )


def build_matrix(paths: Iterable[str], *, full: bool = False) -> dict[str, list[dict[str, object]]]:
    """Map changed paths to independent CI lanes.

    ``paths`` may be all tracked paths in full mode.  The baseline lanes are
    always present so an empty diff or an unknown file type is still checked.
    """

    changed = sorted({normalise_path(path) for path in paths if path.strip()})
    python_paths = [path for path in changed if path.endswith(".py")]
    documentation_paths = [path for path in changed if is_documentation(path)]
    has_allflame = full or any(path.startswith(ALLFLAME_PREFIX) for path in changed)
    has_ledger = full or any(path.startswith(LEDGER_PREFIXES) for path in changed)
    has_docs = bool(documentation_paths)
    has_unknown = any(not is_known_path(path) for path in changed)

    lanes: list[dict[str, object]] = [
        {
            "name": "python-baseline-windows",
            "os": "windows-latest",
            "kind": "python-baseline",
            "paths": python_paths,
            "reason": "full" if full else "unknown" if has_unknown else "changed-python",
        },
        {
            "name": "python-baseline-linux",
            "os": "ubuntu-latest",
            "kind": "python-baseline",
            "paths": python_paths,
            "reason": "full" if full else "unknown" if has_unknown else "changed-python",
        },
    ]
    if has_allflame:
        lanes.append(
            {
                "name": "poe-allflame-pytest",
                "os": "windows-latest",
                "kind": "allflame",
                "paths": [path for path in changed if path.startswith(ALLFLAME_PREFIX)],
                "reason": "full" if full else "allflame-change",
            }
        )
    if has_ledger:
        lanes.append(
            {
                "name": "poe-ledger-static-smoke",
                "os": "windows-latest",
                "kind": "ledger",
                "paths": [
                    path
                    for path in changed
                    if path.startswith(LEDGER_PREFIXES)
                ],
                "reason": "full" if full else "ledger-change",
            }
        )
    if has_docs:
        lanes.append(
            {
                "name": "documentation-links",
                "os": "ubuntu-latest",
                "kind": "docs",
                "paths": documentation_paths,
                "reason": "documentation-change",
            }
        )
    return {"include": lanes}


def git_paths(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False
    )
    return result.stdout.splitlines() if result.returncode == 0 else []


def is_commit(revision: str) -> bool:
    return bool(revision) and not set(revision) == {"0"} and bool(
        git_paths("rev-parse", "--verify", f"{revision}^{{commit}}")
    )


def changed_paths(base: str, head: str, *, full: bool) -> list[str]:
    if full:
        return git_paths("ls-files")
    if is_commit(base):
        return git_paths("diff", "--name-only", "--diff-filter=ACMR", base, head)
    # A new branch has no usable ``before`` SHA.  Compare its tip to its
    # parent instead of suppressing CI altogether.
    parent = git_paths("rev-parse", "--verify", f"{head}^")
    if parent:
        return git_paths("diff", "--name-only", "--diff-filter=ACMR", parent[0], head)
    return git_paths("show", "--format=", "--name-only", head)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--full", choices=("true", "false"), default="false")
    args = parser.parse_args()
    matrix = build_matrix(changed_paths(args.base, args.head, full=args.full == "true"), full=args.full == "true")
    print(f"matrix={json.dumps(matrix, separators=(',', ':'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
