# CLI design

The product is a selected test lane or an exact file location that needs attention. No website is required.

The selector emits one compact `matrix=` line. Scripts return zero for passing checks and nonzero for failure. Compilation and documentation paths resolve under an explicit repository root and reject traversal outside it. Compilation never imports dependencies or writes bytecode.

Default roots follow the scripts' checkout, not the caller's working directory. The selector alone follows the current Git checkout because its input is a revision comparison. The credential scanner reads tracked files and hides matching values.

Documentation runs from purpose to a copyable smoke run, input/output table, repository map and adaptation limits. Examples use actual paths and expected receipts. Workspace-specific lanes remain visible rather than being described as universal CI coverage.

Standalone CLI tests run from unrelated temporary directories, catch broken syntax and escaped paths, check missing documentation and exercise the absent-ledger explanation. Credential tests cover matching and allowed fixture lines. Run `python -m pytest tests -q` and the three smoke commands in README.

Editorial check: no named emotions or unsupported outcome claims. Rejected phrases: "seamless automation", "robust solution", "supercharge your workflow". Personal-cost, sensory and arbitrary-number quotas do not fit a CLI guide and were not invented. Unresolved: Markdown title/space handling is limited and remote links are not checked.
