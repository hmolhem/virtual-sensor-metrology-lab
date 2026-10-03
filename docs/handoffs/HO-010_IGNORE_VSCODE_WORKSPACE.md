# HO-010 — Ignore Local VS Code Workspace

## Branch

`chore/ignore-vscode-workspace`

## Purpose

Prevent local Visual Studio Code workspace metadata from appearing as untracked repository content.

## Change

The repository-level `.gitignore` now explicitly ignores:

```text
.vscode/
```

This keeps editor-specific local configuration outside version control while preserving the existing project protection rules for private simulator truth and generated verification fixtures.

## Verification

Documentation and diff review confirmed that the change is limited to the VS Code ignore rule and its explanatory comment. No simulator code, public/private configuration, verification logic, hidden personality, experiment design, or generated dataset content was modified.

## Outcome

After updating local `main`, a local `.vscode/` directory should no longer appear in `git status`.

## Next step

Proceed to the full synthetic measurement campaign using the frozen hidden laboratory personality and the verified experimental design.
