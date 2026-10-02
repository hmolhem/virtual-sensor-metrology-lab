# Project Architecture — Synthetic Sensor Metrology Lab

## Purpose

This repository implements a **virtual metrology laboratory** for generating realistic synthetic sensor-measurement campaigns.

It does **not** own the downstream DS 7140 analyst workflow. Its responsibility ends at the release of analyst-facing measurements and accompanying public metadata.

## Laboratory measurement chain

```text
Experiment Plan
    -> Environmental Chamber
    -> Local Physical Environment
    -> Reference Instrument / DUT
    -> DAQ and Timing
    -> Analyst-Facing Raw Measurements
    -> Dataset Release Package
```

A separate simulator-only truth path exists in parallel:

```text
Hidden Physical / Error Model
    -> Private Ground Truth
```

## Core subsystems

- **Chamber**: setpoint dynamics, stability, spatial nonuniformity, and temperature conditions.
- **Reference instrument**: calibrated reference response, finite resolution, repeatability, bias, drift, and dynamics.
- **DUT**: offset, sensitivity error, nonlinearity, temperature influence, interaction, hysteresis, repeatability, run/day effects, drift, quantization, and dynamic response.
- **DAQ**: sampling interval, timestamps, synchronization, missing samples, and logged channels.
- **Experiment runner**: static, repeatability, reproducibility, hysteresis, step, ramp, cyclic, sinusoidal, and stability experiments.
- **Release layer**: packages analyst-visible data and public metadata for use outside the simulator repository.

## Verification-before-generation rule

The simulator must be verified before it is used to generate the final measurement campaign.

Completed gates:

- `SV-001`: static generator verification — PASS.
- `SV-002`: dynamic generator verification — PASS.
- `ED-001`: experimental-design verification — PASS.

Only after these gates pass, and after the public/private configuration boundary is finalized, will the hidden DUT/reference/chamber parameter set be frozen and the final analyst dataset generated.

## Information domains

### Private simulator truth

Simulator-only values such as true RH, injected error components, exact dynamic parameters, latent chamber states, and exact DUT/reference/chamber error parameters.

### Public laboratory output

Laboratory-like measurements and public metadata visible to a validation engineer. These include Test IDs, setpoints, timestamps, DUT/reference readings, and declared instrument/chamber specifications.

### Downstream analysis products

Processed datasets, fitted calibration models, ANOVA tables, uncertainty budgets, compliance decisions, plots, notebooks, and course reports belong in the future DS 7140 repository, not here.

## Repository boundary

```text
THIS REPOSITORY
Virtual Lab -> Verified Measurement Campaign -> Released Dataset

SEPARATE FUTURE REPOSITORY
Released Dataset -> DS7140 Analysis -> Report
```

The downstream project may later compare analyst estimates with sealed simulator truth as a final audit, but simulator truth is not part of the analyst-facing starting dataset.

## Repository workflow

Every unit of work follows:

```text
new task-specific branch
-> implementation
-> verification
-> handoff
-> HANDOFF_INDEX update
-> PROJECT_HISTORY update
-> pull request
-> merge
```

No direct development changes are made on `main`.
