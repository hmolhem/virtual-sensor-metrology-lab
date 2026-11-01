# Virtual Sensor Metrology Lab

A reproducible virtual metrology laboratory for generating physics-informed synthetic measurement datasets for sensor validation, calibration, dynamics, stability, and uncertainty studies.

This repository is the **laboratory and dataset-generation system**. It is intentionally separate from the downstream **analyst-side sensor-validation repository**.

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

The following work belongs to the separate **downstream analysis repository**:

- exploratory data analysis
- analyst-side statistical characterization
- ANOVA and variance-component analysis
- calibration-model fitting and model selection
- blind validation
- dynamic-response analysis from the released measurements
- stability/drift analysis
- measurement-uncertainty budget and Monte Carlo propagation
- compliance decisions
- analysis notebooks, figures, tables, and reporting artifacts

Simulator verification calculations may appear here, but they exist only to prove that the virtual laboratory behaves as intended. They are not substitutes for the downstream analysis.

## Quick Start

Install the public verification environment:

```bash
python -m pip install -r requirements.txt
```

Run public checks:

```bash
pytest -q
python verification/DR-002_Cross_Platform_Release_Integrity/dr002_cross_platform_release_integrity.py
```

The GitHub Actions public-verification workflow also runs the public boundary, experimental-design, simulator, and release-integrity gates.

The public verification environment is pinned to the exact package versions exercised by the successful 2026-10-31 audit run. CI runs on pull requests, pushes to `main`, and manual dispatch. It also runs Ruff static checks before the verification gates. Ruff rule B023 is explicitly ignored because the reported loop-binding warning was reviewed as a false positive for the current implementation; no late-bound loop-variable defect was identified.

Two gates intentionally depend on simulator-only local configuration:

- `HP-001` — hidden-personality verification;
- `MC-001` — full campaign regeneration.

On a public clone these gates now report `SKIPPED` with an explanatory message rather than raising a raw traceback. Public reproducibility is provided by the frozen release commitments and DR-002.

## Information boundary

### Public / analyst-visible

The downstream analysis repository may receive:

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

The formal handoff from this laboratory to the separate downstream project is `data/generated/`.

The canonical frozen release package is:

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
    release_commitment_v1_1.json
    README.md
```

The canonical analyst-facing release is:

```text
VSM-LAB-DATA-v1.1
```

This is a corrective release of historical `VSM-LAB-DATA-v1`; the seven measurement/design CSV payload commitments are unchanged. The correction establishes canonical LF line endings and a byte-reproducible manifest commitment.

Canonical dataset-manifest SHA-256:

```text
efd9e79958b9d7c7b8730ee9015c72c3e8205effd03c686ff58b03454188f847
```

The historical v1 commitment remains tracked for provenance in `data/generated/release_commitment_v1.json`.

Public specifications and release metadata accompany the dataset under `config/public/` and in the manifest.

The downstream analysis repository starts from this frozen release package and does not depend on simulator internals.

For the formal laboratory-to-analysis contract, see `docs/02_LAB_TO_DS7140_INTERFACE.md`.

## Verified engineering baseline

The laboratory baseline has passed the following gates:

- `SV-001` — static generator verification: **PASS (8/8)**
- `SV-002` — dynamic generator verification: **PASS (10/10)**
- reusable simulator-core regression verification: **PASS**
- `ED-001` — experimental-design matrix verification: **PASS (11/11)**
- `CB-001` — public/private configuration-boundary verification: **PASS (11/11)**
- `HP-001` — hidden laboratory personality commitment: **PASS (8/8)**
- `MC-001` — full synthetic measurement campaign: **PASS (8/8)**
- `DR-001` — historical v1 dataset-release gate: **PASS (10/10) on v1; SKIPPED on current v1.1**
- `DR-002` — canonical v1.1 cross-platform corrective-release integrity verification: **PASS (11/11)**

## Frozen Release Design Limitations

The canonical `VSM-LAB-DATA-v1.1` release is intentionally frozen. The following limitations are therefore documented rather than retroactively changed:

- the dynamic-step chamber/reference response is slower than the public DUT `t90 <= 60 s` requirement, so direct DUT-only t90 compliance cannot be demonstrated from this campaign;
- the stability campaign spans 90 days, so annual drift compliance cannot be demonstrated without unsupported extrapolation;
- the released static temperature channels use the same rounded local temperature indication for DUT and reference, so independent temperature-channel measurement error is not represented;
- static records are released only after the campaign has entered the declared `STABLE` state; transient chamber-state behavior is characterized in the dedicated dynamic families.

A future release may extend these design dimensions, but doing so requires a new release identifier and a new verification/freeze cycle.

## Current stage

The first Virtual Sensor Metrology Lab release cycle and its cross-platform provenance correction are complete.

```text
Verified simulator core
        -> Verified experimental design
        -> Verified public/private configuration boundary
        -> Frozen hidden DUT/reference/chamber personality
        -> Full synthetic measurement campaign
        -> Historical VSM-LAB-DATA-v1 freeze
        -> DR-002 cross-platform integrity correction
        -> VSM-LAB-DATA-v1.1 FROZEN
        -> Separate downstream analysis repository   [NEXT]
```

No further analysis of sensor performance belongs in this repository unless it is needed to verify the laboratory itself.

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

**Role:** Virtual laboratory + frozen synthetic measurement dataset generation

**Canonical frozen release:** `VSM-LAB-DATA-v1.1`

**Release-integrity gate:** `DR-002 = PASS (11/11)`

**Downstream consumer:** separate downstream analysis repository

For chronological status, see `docs/PROJECT_HISTORY.md`.
