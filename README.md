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

All repository changes are made on a task-specific branch. No direct development work is performed on `main`. Each completed task must include an English handoff document under `docs/handoffs/`, and every handoff must be registered in `docs/handoffs/HANDOFF_INDEX.md` before the pull request is opened.

## Core separation

The project distinguishes three data layers:

1. **Simulation truth** — private ground truth used only to verify the simulator.
2. **Raw laboratory-like measurements** — the public/analyst view of the experiment.
3. **Processed analysis data** — derived datasets used for statistics, calibration, validation, and uncertainty analysis.

Final hidden simulator truth must not be committed to the repository.

## Current milestone

`SV-001` verifies the static synthetic-data generator before any full project dataset is created.
