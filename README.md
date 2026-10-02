# Full Sensor Validation & Metrology

A full static and dynamic sensor validation and metrology project using physics-informed synthetic data, calibration, ANOVA, uncertainty analysis, and Monte Carlo methods.

## Project objective

Build a reproducible synthetic measurement system for an HVAC relative-humidity sensor and use it to study the complete validation chain:

- measurement-system definition and requirements
- static characterization
- repeatability and reproducibility
- hysteresis, linearity, and temperature influence
- calibration and independent validation
- dynamic response and parameter estimation
- stability and drift
- ANOVA and variance components
- measurement uncertainty and Monte Carlo propagation
- compliance decisions

## Development rule

All repository changes are made on a task-specific branch. No direct development work is performed on `main`.

Every completed task must include all three continuity records before its pull request is finalized:

1. an English handoff document under `docs/handoffs/`
2. a registered entry in `docs/handoffs/HANDOFF_INDEX.md`
3. a concise chronological entry in `docs/PROJECT_HISTORY.md`

The handoff contains detailed engineering continuity, the handoff index is the authoritative registry, and the project history is the compact chronological ledger.

## Core separation

The project distinguishes three data layers:

1. **Simulation truth** — private ground truth used only to verify the simulator.
2. **Raw laboratory-like measurements** — the public/analyst view of the experiment.
3. **Processed analysis data** — derived datasets used for statistics, calibration, validation, and uncertainty analysis.

Final hidden simulator truth must not be committed to the repository.

## Current milestone

Completed and verified milestones:

- `SV-001` — static generator verification: **PASS (8/8)**
- `SV-002` — dynamic generator verification: **PASS (10/10)**
- reusable simulator-core refactor with SV-001/SV-002 regression verification: **PASS**
- `ED-001` — experimental-design matrix verification: **PASS (11/11)**

The current engineering baseline includes verified simulator physics, reusable core modules, and a predefined static/dynamic/stability/uncertainty test matrix.

The next technical milestone is to define the final public/private configuration boundary and freeze the hidden DUT/reference/chamber parameter set before generating the full synthetic validation dataset.

For chronological project status, see `docs/PROJECT_HISTORY.md`.
