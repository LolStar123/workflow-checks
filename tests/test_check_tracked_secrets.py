from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "check_tracked_secrets.py"
)
SPEC = importlib.util.spec_from_file_location("check_tracked_secrets", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def findings(text: str) -> list[tuple[int, str]]:
    return list(MODULE.scan_text(text))


def test_detects_path_of_exile_session_literal() -> None:
    token = "POE" + "SESSID = " + '"' + ("a" * 32) + '"'
    assert findings(token) == [(1, "path-of-exile-session")]


def test_detects_private_key_without_echoing_its_body() -> None:
    marker = "-----BEGIN " + "PRIVATE KEY-----"
    assert findings(marker) == [(1, "private-key")]


def test_environment_lookup_is_safe() -> None:
    assert findings('POESESSID = os.environ.get("POESESSID", "")') == []


def test_explicit_allow_marker_suppresses_fixture() -> None:
    token = "CF_" + "CLEARANCE = " + '"' + ("b" * 24) + '"'
    assert findings(f"{token}  # secret-scan: allow") == []
