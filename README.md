# Workflow checks

Select test lanes for a mixed Python workspace, compile changed Python files without importing them, and catch broken local documentation links before a commit lands.

These are command-line checks. Their output is a GitHub Actions matrix or a short pass/fail receipt; they need no server or browser.

## Start here

Python 3.10+ and Git are required. Scripts use the standard library; only tests need pytest.

```sh
git clone https://github.com/LolStar123/workflow-checks.git
cd workflow-checks
python -m pip install pytest
python -m pytest tests -q
python scripts/compile_paths.py
python scripts/check_docs_links.py
python scripts/check_tracked_secrets.py
```

Expected output from the three smoke commands:

```text
compiled scripts/detect_ci_matrix.py
documentation link check passed
Tracked credential scan passed.
```

A failed check exits nonzero. Compilation reads source without importing dependencies or writing bytecode. The secret scan prints rule names and file locations, never matching values.

## Pick a check

| Command | Input | Output |
|---|---|---|
| `python scripts/detect_ci_matrix.py --full true` | Tracked paths in the current Git checkout | One `matrix={"include":[...]}` line |
| `python scripts/detect_ci_matrix.py --base BASE_SHA --head HEAD` | Changes between two Git revisions | Lanes with runner, check kind, paths and reason |
| `python scripts/compile_paths.py` | Default selector script, or `TARGETS_JSON` | Compiled paths or syntax/missing-path failures |
| `python scripts/check_docs_links.py` | README by default, or `TARGETS_JSON` | Broken local paths or a pass receipt |
| `python scripts/check_tracked_secrets.py` | Tracked text files | Credential-pattern locations or a pass receipt |
| `python scripts/ledger_smoke.py --root /path/to/original/workspace` | Original `poe/poe-ledger` and `poe/faustus_flips` directories | Static Python and HTML-asset linkage check |

The selector runs from the Git checkout being selected. Other checks default to this script checkout, even when launched from another working directory; pass `--root` to check another repository.

For explicit paths in PowerShell:

```powershell
$env:TARGETS_JSON = '["scripts/detect_ci_matrix.py", "scripts/compile_paths.py"]'
python scripts/compile_paths.py
$env:TARGETS_JSON = '["README.md", "DESIGN.md"]'
python scripts/check_docs_links.py
Remove-Item Env:TARGETS_JSON
```

`--paths-json` overrides the environment for compilation and documentation checks. For another checkout, pass `--root` and explicit paths together rather than relying on the compile smoke default.

## Repository map

| Path | Responsibility |
|---|---|
| [scripts/detect_ci_matrix.py](scripts/detect_ci_matrix.py) | Domain-to-lane routing and revision fallback |
| [scripts/compile_paths.py](scripts/compile_paths.py) | Syntax checks constrained to the chosen repository |
| [scripts/check_docs_links.py](scripts/check_docs_links.py) | Local Markdown path checks |
| [scripts/check_tracked_secrets.py](scripts/check_tracked_secrets.py) | Small credential-pattern scanner |
| [scripts/ledger_smoke.py](scripts/ledger_smoke.py) | Original workspace-specific ledger check |
| [tests](tests) | Lane selection, credential patterns and standalone CLI regressions |
| [.github/workflows/tests.yml](.github/workflows/tests.yml) | pytest and credential scan on main pushes and PRs |
| [DESIGN.md](DESIGN.md) | CLI contracts and adaptation boundaries |

## Adopting it elsewhere

Start with the selector's domain rules. Its lane names, Windows runners and ledger paths describe the originating workspace; copying the scripts does not make those projects exist in your repository. The included workflow checks this repository; an emitted matrix needs a separate caller workflow.

The documentation checker validates file existence, not remote URLs or heading anchors, and its Markdown parser is deliberately small. The credential scanner complements a dedicated scanner and can miss formats outside its rule set. The ledger check fails with an explanation when its original directories are absent.
