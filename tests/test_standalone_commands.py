"""Exercise the public CLI from unrelated working directories and isolated roots."""
import json
from pathlib import Path
import subprocess
import sys

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def run(name, cwd, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / name), *args], cwd=cwd,
                          capture_output=True, text=True)


def test_compile_default_uses_checkout_not_parent_or_cwd(tmp_path):
    result = run("compile_paths.py", tmp_path)
    assert result.returncode == 0, result.stderr
    assert "compiled scripts/detect_ci_matrix.py" in result.stdout


def test_compile_reports_real_syntax_and_escape_failures(tmp_path):
    (tmp_path / "valid.py").write_text("answer = 42\n")
    (tmp_path / "broken.py").write_text("def broken(\n")
    assert run("compile_paths.py", tmp_path, "--root", str(tmp_path),
               "--paths-json", json.dumps(["valid.py"])).returncode == 0
    result = run("compile_paths.py", tmp_path, "--root", str(tmp_path),
                 "--paths-json", json.dumps(["broken.py", "../outside.py"]))
    assert result.returncode != 0
    assert "broken.py" in result.stderr and "outside repository" in result.stderr


def test_docs_follow_local_links_and_reject_missing_or_outside_pages(tmp_path):
    (tmp_path / "guide.md").write_text("[Good](file.txt) [Remote](https://example.org)\n")
    (tmp_path / "file.txt").write_text("fixture\n")
    args = ("--root", str(tmp_path), "--paths-json", json.dumps(["guide.md"]))
    assert run("check_docs_links.py", tmp_path, *args).returncode == 0
    (tmp_path / "file.txt").unlink()
    assert "broken local link" in run("check_docs_links.py", tmp_path, *args).stderr
    result = run("check_docs_links.py", tmp_path, "--root", str(tmp_path),
                 "--paths-json", json.dumps(["missing.md", "../outside.md"]))
    assert "missing documentation" in result.stderr and "outside repository" in result.stderr


def test_ledger_without_original_projects_explains_required_root(tmp_path):
    result = run("ledger_smoke.py", tmp_path)
    assert result.returncode != 0
    assert "Pass --root" in result.stderr
    assert "Traceback" not in result.stderr


def test_secret_default_uses_checkout_instead_of_unrelated_cwd(tmp_path):
    result = run("check_tracked_secrets.py", tmp_path)
    assert result.returncode == 0, result.stderr
    assert "Tracked credential scan passed" in result.stdout


def test_docs_default_checks_readme_in_explicit_root(tmp_path):
    result = run("check_docs_links.py", tmp_path, "--root", str(tmp_path))
    assert result.returncode != 0
    assert "missing documentation: README.md" in result.stderr
