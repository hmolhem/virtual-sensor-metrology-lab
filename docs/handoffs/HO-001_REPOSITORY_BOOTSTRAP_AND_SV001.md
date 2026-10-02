# HO-001 — Repository Bootstrap and SV-001 Static Verification

## Milestone identity

- Project: Full Sensor Validation & Metrology
- Branch: `chore/bootstrap-repository-structure`
- Date: 2026-10-01
- Scope: Initial repository organization, workflow policy, and import of the verified SV-001 static simulator fixture

## Objective

Establish a repository structure that supports a verification-first sensor-metrology workflow while protecting final hidden simulator truth and preventing direct development on `main`.

## Work completed

1. Expanded the project README with the project objective, data-layer separation, current milestone, and branch/PR/handoff policy.
2. Updated `.gitignore` so final private simulator truth remains local and is not committed.
3. Added the project architecture document describing the chamber, reference, DUT, DAQ, experiment-runner, and public/private data paths.
4. Added an authoritative handoff index under `docs/handoffs/HANDOFF_INDEX.md`.
5. Added the SV-001 static verification fixture and its generated verification artifacts.
6. Confirmed that SV-001 passes all eight verification checks before proceeding to dynamic verification.

## SV-001 verification checks

| Test | Purpose | Result |
|---|---|---|
| SV-001A | Deterministic DUT offset | PASS |
| SV-001B | Deterministic reference bias | PASS |
| SV-001C | DUT/reference quantization | PASS |
| SV-001D | Repeatability-noise statistics | PASS |
| SV-001E | Chamber-stability statistics | PASS |
| SV-001F | Hierarchical day/run/noise structure | PASS |
| SV-001G | Fixed-seed reproducibility | PASS |
| SV-001H | Private/public field separation | PASS |

## Key design decisions

- Simulation truth and analyst data are treated as different data products.
- Final hidden DUT truth is never committed to the repository.
- Verification fixtures may expose known truth because their purpose is to verify simulator correctness.
- Day effects are sampled once per day, run effects once per run, and repeatability noise once per observation so later ANOVA and variance-component analyses remain meaningful.
- Full project datasets will not be generated until both static and dynamic simulator-verification gates pass.

## Repository workflow rule

Every future unit of work must follow:

```text
create task branch
-> implement only on that branch
-> verify
-> create/update English handoff
-> update handoff index
-> open pull request to main
-> merge only after review/acceptance
```

No direct development work is permitted on `main`.

## Next milestone

`SV-002 — Dynamic Generator Verification`

The next task will use a known first-order dynamic fixture to verify time constant, dead time, step-response thresholds, chamber/reference/DUT dynamics, and sampling effects before the final hidden DUT is frozen.
