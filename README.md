# Virtual Sensor Metrology Lab

A reproducible virtual metrology laboratory for generating physics-informed synthetic measurement datasets for sensor validation, calibration, dynamics, stability, and uncertainty studies.

This repository is the **laboratory and dataset-generation system**. It is intentionally separate from the downstream **DS 7140 data-science analysis project**.

## Scope

The laboratory models the complete measurement chain:

```text
Experiment Plan
    -> Environmental Chamber
    -> Local Physical Environment
    -> Reference Instrument + DUT
    -> DAQ / Timing
    -> Analyst-Facing Measurements
    -> Frozen Dataset Release
```

A separate simulator-only path preserves hidden truth:

```text
Hidden Physical / Error Model
    -> Private Simulator Truth
```

The current implementation is configured for an HVAC relative-humidity sensor, but the architecture is designed to be reusable for other sensor-validation problems.

## What this repository owns

- environmental-chamber behavior and local measurement conditions
- reference-instrument behavior
- DUT/sensor static and dynamic behavior
- DAQ, sampling, timing, and quantization
- controlled random effects, drift, hysteresis, nonlinearity, temperature effects, and repeatability
- experimental-design and test-matrix generation
- simulator verification against known fixtures
- public/private information separation
- final synthetic measurement campaign
- frozen analyst-facing dataset release and provenance metadata

## What this repository does not own

The following work belongs to the future **DS 7140 course-project repository** and will begin only after the laboratory releases a frozen dataset:

- exploratory data analysis
- analyst-side statistical characterization
- ANOVA and variance-component analysis
- calibration-model fitting and model selection
- blind validation
- dynamic-response analysis from the released measurements
- stability/drift analysis
- measurement-uncertainty budget and Monte Carlo propagation
- compliance decisions
- course notebooks, figures, tables, and final report

Simulator verification calculations may appear here, but they exist only to prove that the virtual laboratory behaves as intended. They are not substitutes for the downstream DS 7140 analysis.

## Information boundary

### Public / analyst-visible

The future course repository may receive:

- DUT public specification and acceptance limits
- reference-instrument public specification
- chamber public specification
- Test IDs and experimental design
- setpoints and logged environmental conditions
- timestamps and measured channels
- dataset manifest, schema, and provenance

The canonical public laboratory specification is tracked at:

```text
config/public/lab_spec_v1.json
```

### Private / simulator-only

The analyst must not receive the exact hidden values used to create the synthetic sensor behavior, including:

- DUT offset, gain error, nonlinearity, hysteresis, and temperature coefficients
- true dynamic time constants and dead time
- exact drift law and random-effect parameters
- reference-instrument hidden bias/error parameters
- chamber hidden bias/nonuniformity/error parameters
- latent true environmental states and injected error components

Final private simulator configuration is restricted to local files under `config/private/`, while simulator-only truth products are restricted to local files under `data/private_truth/`. Both paths are protected by `.gitignore`.

The executable boundary policy is implemented in `src/config_boundary.py`, which validates public configuration, restricts private truth loading to the protected directory, and blocks simulator-only field names from analyst-facing serialized payloads.

## Dataset release boundary

The formal handoff from this laboratory to the future DS 7140 project is `data/generated/`.

The intended release package is:

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

Public specifications and release metadata may accompany the dataset under `config/public/` and in the manifest.

The downstream DS 7140 repository starts from this frozen release package and does not depend on simulator internals.

For the formal laboratory-to-course-project contract, see `docs/02_LAB_TO_DS7140_INTERFACE.md`.

## Verified engineering baseline

The current laboratory baseline has passed the following gates:

- `SV-001` — static generator verification: **PASS (8/8)**
- `SV-002` — dynamic generator verification: **PASS (10/10)**
- reusable simulator-core regression verification: **PASS**
- `ED-001` — experimental-design matrix verification: **PASS (11/11)**
- `CB-001` — public/private configuration-boundary verification: **PASS (11/11)**

This means the simulator core, predefined experimental design, and analyst/private information boundary have been verified before final hidden sensor truth is frozen.

## Current stage

The project remains in the **virtual-laboratory construction phase**. The final course dataset has **not** been generated yet.

Current sequence:

```text
Verified simulator core
        -> Verified experimental design
        -> Verified public/private configuration boundary
        -> Freeze hidden DUT/reference/chamber truth   [NEXT]
        -> Run full synthetic measurement campaign
        -> Freeze analyst-facing dataset release
        -> Create separate DS 7140 analysis repository
```

The next engineering milestone will define the final hidden laboratory personality without exposing it to the future analyst-facing data path.

## Development workflow

No development work is performed directly on `main`.

Every completed task follows:

```text
new task-specific branch
-> technical/documentation work
-> verification
-> English handoff
-> HANDOFF_INDEX update
-> PROJECT_HISTORY update
-> pull request
-> merge to main
```

Project continuity is maintained through three records:

1. `docs/PROJECT_HISTORY.md` — concise chronological engineering history
2. `docs/handoffs/HANDOFF_INDEX.md` — authoritative handoff registry
3. `docs/handoffs/HO-xxx_*.md` — detailed task-level handoffs

## Repository status

**Repository:** `hmolhem/virtual-sensor-metrology-lab`

**Role:** Virtual laboratory + synthetic measurement dataset generation

**Downstream consumer:** A separate DS 7140 repository created only after the first frozen dataset release

For chronological status, see `docs/PROJECT_HISTORY.md`.
