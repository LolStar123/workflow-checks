#!/usr/bin/env python3
"""Offline static smoke checks for the PoE ledger and its Faustus linkage."""

from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "poe" / "poe-ledger"
FAUSTUS = ROOT / "poe" / "faustus_flips"
ASSET_LINK = re.compile(r"(?:src|href)\s*=\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)


def check_python() -> list[str]:
    failures: list[str] = []
    source_files = [LEDGER / "server.py", LEDGER / "fetch_transfig_data.py", *FAUSTUS.glob("*.py")]
    for source in source_files:
        try:
            ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        except (OSError, SyntaxError, UnicodeDecodeError) as error:
            failures.append(f"Python syntax: {source.relative_to(ROOT)}: {error}")
    server_source = (LEDGER / "server.py").read_text(encoding="utf-8")
    if "SimpleHTTPRequestHandler" not in server_source:
        failures.append("server.py no longer exposes a static file handler")
    if "faustus_flips" not in server_source or not (FAUSTUS / "__init__.py").is_file():
        failures.append("server.py's Faustus package link is missing")
    return failures


def check_static_links() -> list[str]:
    failures: list[str] = []
    for page in LEDGER.glob("*.html"):
        for link in ASSET_LINK.findall(page.read_text(encoding="utf-8")):
            target = link.split("#", 1)[0].split("?", 1)[0]
            # Template literals are populated at runtime and are not static
            # files the HTTP handler can validate here.
            if "${" in target or not target or target.startswith(("/", "http:", "https:", "//", "data:", "mailto:")):
                continue
            if not (page.parent / target).resolve().is_file():
                failures.append(f"broken static link: {page.relative_to(ROOT)} -> {link}")
    return failures


def main() -> int:
    failures = check_python() + check_static_links()
    if failures:
        raise SystemExit("\n".join(failures))
    print("PoE ledger static-link smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
