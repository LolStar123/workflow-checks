from pathlib import Path
import sys


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from detect_ci_matrix import build_matrix  # noqa: E402


def lanes_for(paths, **kwargs):
    return {lane["kind"]: lane for lane in build_matrix(paths, **kwargs)["include"]}


def test_allflame_change_gets_windows_pytest_and_python_baselines():
    lanes = lanes_for(["poe/allflame/classify.py"])
    assert lanes["allflame"]["os"] == "windows-latest"
    assert lanes["python-baseline"]["paths"] == ["poe/allflame/classify.py"]
    assert len([lane for lane in build_matrix(["poe/allflame/classify.py"])["include"] if lane["kind"] == "python-baseline"]) == 2


def test_ledger_and_docs_changes_select_their_specialised_lanes():
    lanes = lanes_for(["poe/poe-ledger/server.py", "poe/README.md"])
    assert lanes["ledger"]["os"] == "windows-latest"
    assert lanes["docs"]["paths"] == ["poe/README.md"]


def test_unknown_changes_still_get_a_baseline_lane():
    matrix = build_matrix(["new-component/client.ts"])
    baseline_lanes = [lane for lane in matrix["include"] if lane["kind"] == "python-baseline"]
    assert len(baseline_lanes) == 2
    assert {lane["reason"] for lane in baseline_lanes} == {"unknown"}


def test_dot_prefixed_paths_keep_their_repository_name():
    lanes = lanes_for(["./.github/scripts/detect_ci_matrix.py"])
    assert lanes["python-baseline"]["paths"] == [".github/scripts/detect_ci_matrix.py"]


def test_full_matrix_includes_poe_lanes():
    lanes = lanes_for(["README.md", "poe/allflame/classify.py"], full=True)
    assert {"allflame", "ledger", "docs", "python-baseline"} <= set(lanes)
