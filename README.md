# Synthetic Sensor Metrology Lab

A reproducible virtual metrology laboratory for generating physics-informed synthetic measurement data for sensor validation studies.

> Historical note: this repository was originally created as **Full Sensor Validation & Metrology**. Its scope is now intentionally narrower: build and verify the synthetic laboratory, run the measurement campaign, and release analyst-facing datasets. The downstream DS 7140 analysis will live in a separate repository.

## Repository purpose

This repository owns the **measurement-system side** of the project:

- environmental chamber simulation
- reference-instrument simulation
- DUT/sensor simulation
- DAQ and timing behavior
- static and dynamic physics
- hidden error mechanisms and private simulator truth
- experimental-design / test-matrix generation
- simulator verification
- final synthetic measurement campaign
- analyst-facing dataset release and metadata

The current laboratory is configured around an HVAC relative-humidity sensor, but the architecture is intended to be reusable for additional sensor types.

## Explicitly out of scope

The following belong to the future **DS 7140 course-project repository**, not to this laboratory repository:

- exploratory data analysis of the released dataset
- statistical characterization as an analyst
- ANOVA / variance-component analysis
- calibration-model fitting
- blind validation of fitted calibration models
- uncertainty-budget analysis from the analyst perspective
- Monte Carlo uncertainty propagation for the course analysis
- final compliance conclusions
- course notebooks, figures, tables, and report

The laboratory may contain verification calculations that prove the simulator behaves correctly. Those verification calculations are not the downstream course analysis.

## System boundary

```text
                 SYNTHETIC SENSOR METROLOGY LAB

Requirements / public specifications
                |
                v
Experimental design / test matrix
                |
                v
Chamber -> local environment -> Reference + DUT -> DAQ
                |                              |
                |                              +-> private simulator truth
                v
Analyst-facing synthetic measurements
                |
                v
Dataset release package
                |
                +-------------------------------------->
                                                        FUTURE DS 7140 REPOSITORY
                                                        EDA / statistics / calibration
                                                        validation / uncertainty / report
```

## Public/private separation

Two information domains are intentionally separated.

### Public / analyst-visible

- DUT public specification and acceptance limits
- reference-instrument public specification
- chamber public specification
- experimental design and Test IDs
- setpoints and logged environmental conditions
- timestamps and measured channels
- dataset manifest and provenance

### Private / simulator-only

- exact DUT offset, gain error, nonlinearity, hysteresis and temperature coefficients
- exact dynamic time constants and dead time
- exact drift law and random-effect parameters
- exact reference bias/error parameters
- exact chamber bias/nonuniformity/error parameters
- latent true environmental states and injected error components

Final hidden simulator truth must not be committed to the public/tracked analyst-facing data path. It remains local/private to the laboratory.

## Dataset handoff contract

When the synthetic measurement campaign is complete, this repository will produce a release package under `data/generated/` containing only analyst-appropriate information. The intended package includes:

```text
data/generated/
    static_measurements.csv
    dynamic_step_measurements.csv
    ramp_measurements.csv
    cyclic_measurements.csv
    sinusoidal_measurements.csv
    stability_measurements.csv
    test_matrix.csv
    dataset_manifest.json
    README.md
```

Public specifications and other release metadata may accompany that package under `config/public/` or within the release manifest.

The future DS 7140 repository will start from this released measurement package rather than from simulator internals.

## Development rule

All repository changes are made on a task-specific branch. No direct development work is performed on `main`.

Every completed task must include all three continuity records before its pull request is finalized:

1. an English handoff document under `docs/handoffs/`
2. a registered entry in `docs/handoffs/HANDOFF_INDEX.md`
3. a concise chronological entry in `docs/PROJECT_HISTORY.md`

Required workflow:

```text
new task-specific branch
-> technical work
-> verification
-> English handoff
-> HANDOFF_INDEX update
-> PROJECT_HISTORY update
-> pull request
-> merge to main
```

## Verified baseline

Completed verification milestones:

- `SV-001` — static generator verification: **PASS (8/8)**
- `SV-002` — dynamic generator verification: **PASS (10/10)**
- reusable simulator-core refactor with SV-001/SV-002 regression verification: **PASS**
- `ED-001` — experimental-design matrix verification: **PASS (11/11)**

The laboratory therefore has a verified static/dynamic simulation core and a predefined experiment design.

## Current engineering milestone

The next technical milestone is to define and verify the final public/private configuration boundary, then freeze the hidden DUT/reference/chamber parameter set. Only after that will the final synthetic measurement campaign be generated.

For project chronology, see `docs/PROJECT_HISTORY.md`. For the laboratory-to-course-project interface, see `docs/02_LAB_TO_DS7140_INTERFACE.md`.
