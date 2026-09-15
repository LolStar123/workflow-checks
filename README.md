# Workflow checks

Small Python tools for checking a mixed-project repository before changes land.
The CI selector maps changed paths to test lanes, including Windows-specific
projects, documentation checks, and a baseline for unfamiliar directories.

## Tools

- `scripts/detect_ci_matrix.py`: build a GitHub Actions matrix from changed paths.
- `scripts/compile_paths.py`: compile selected Python files without running them.
- `scripts/check_docs_links.py`: check local Markdown links.
- `scripts/check_tracked_secrets.py`: report credential-pattern locations without printing values.
- `scripts/ledger_smoke.py`: a smoke check for the originating workspace's ledger project.

The lane names and ledger smoke check are specific to the original workspace.
Adapt those paths before adopting the tools in another repository. The credential
checker covers a small pattern set; it complements a dedicated secret scanner.
No workflow is enabled automatically.

## Tests

```sh
python -m pip install pytest
python -m pytest tests -q
```

The scripts use the Python standard library. Tests require pytest.
