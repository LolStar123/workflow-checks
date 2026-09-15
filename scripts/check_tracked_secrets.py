"""Fail CI when tracked text files contain high-confidence credential literals.

Only the rule name and source location are reported. Secret values are never
echoed to logs. Add ``secret-scan: allow`` to a deliberately safe fixture line.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable


ALLOW_MARKER = "secret-scan: allow"
RULES = {
    "path-of-exile-session": re.compile(
        r"""(?ix)
        \b(?:POESESSID|CF_CLEARANCE)\s*=\s*
        ["'][^"'\r\n]{8,}["']
        """
    ),
    "literal-cookie-header": re.compile(
        r"""(?ix)
        ["']Cookie["']\s*:\s*["'][^"'\r\n]{16,}["']
        """
    ),
    "literal-password": re.compile(
        r"""(?ix)
        \b(?:password|passwd|pwd)\s*[:=]\s*
        ["'][^"'\r\n]{8,}["']
        """
    ),
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws-access-key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "github-token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "openai-key": re.compile(r"\bsk-[A-Za-z0-9_-]{32,}\b"),
}


def scan_text(text: str) -> Iterable[tuple[int, str]]:
    """Yield one finding per matching rule and line."""
    for line_number, line in enumerate(text.splitlines(), start=1):
        if ALLOW_MARKER in line:
            continue
        for rule_name, pattern in RULES.items():
            if pattern.search(line):
                yield line_number, rule_name


def tracked_paths(repo_root: Path) -> Iterable[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "-z"],
        cwd=repo_root,
    )
    for raw_path in output.split(b"\0"):
        if raw_path:
            yield repo_root / os.fsdecode(raw_path)


def scan_repository(repo_root: Path) -> list[tuple[str, int, str]]:
    findings: list[tuple[str, int, str]] = []
    for path in tracked_paths(repo_root):
        try:
            data = path.read_bytes()
        except (OSError, ValueError):
            continue
        if b"\0" in data:
            continue
        text = data.decode("utf-8", errors="replace")
        relative_path = path.relative_to(repo_root).as_posix()
        for line_number, rule_name in scan_text(text):
            findings.append((relative_path, line_number, rule_name))
    return findings


def main() -> int:
    repo_root = Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
    )
    findings = scan_repository(repo_root)
    if findings:
        print("Potential tracked credential literals found:", file=sys.stderr)
        for path, line_number, rule_name in findings:
            print(f"{path}:{line_number}: {rule_name}", file=sys.stderr)
        return 1
    print("Tracked credential scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
