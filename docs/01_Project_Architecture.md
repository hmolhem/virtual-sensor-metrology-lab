# Project Architecture

## Purpose

This project implements a complete synthetic sensor-validation and metrology workflow for an HVAC relative-humidity sensor. The synthetic system is designed to support realistic measurement analysis rather than arbitrary random-data generation.

## Measurement chain

```text
Experiment Plan
    -> Environmental Chamber
    -> Local Physical Environment
    -> Reference Instrument / DUT
    -> DAQ and Timing
    -> Raw Analyst Dataset
```

A separate simulation-truth path exists only for simulator verification:

```text
Hidden Physical / Error Model
    -> Private Ground Truth
```

## Core subsystems

- **Chamber**: setpoint dynamics, stability, spatial nonuniformity, and temperature conditions.
- **Reference instrument**: calibrated reference response, finite resolution, repeatability, bias, drift, and dynamics.
- **DUT**: offset, sensitivity error, nonlinearity, temperature influence, interaction, hysteresis, repeatability, run/day effects, drift, quantization, and dynamic response.
- **DAQ**: sampling interval, timestamps, synchronization, missing samples, and logged channels.
- **Experiment runner**: static, repeatability, reproducibility, hysteresis, calibration, validation, step, ramp, cyclic, sinusoidal, and stability experiments.

## Verification-before-validation rule

The simulator must be verified before it is used to generate the final project dataset.

- `SV-001`: static generator verification.
- `SV-002`: dynamic generator verification.

Only after these gates pass will the final hidden DUT parameters be frozen and the full analyst dataset generated.

## Data layers

1. **Private truth** — simulator-only values such as true RH, injected error components, and true dynamic parameters.
2. **Raw analyst data** — laboratory-like measurements visible to the validation engineer.
3. **Processed data** — cleaned, summarized, or feature-engineered data used for statistical analysis.

## Repository workflow

Every unit of work follows:

```text
branch -> implementation -> verification -> handoff -> indexed handoff -> pull request -> merge
```

No direct development changes are made on `main`.
