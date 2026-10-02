# HO-004 — Experimental Design Matrix

## Milestone identity

- Project: Full Sensor Validation & Metrology
- Branch: `feature/experimental-design-matrix`
- Date: 2026-10-01
- Scope: Implement and verify the project-level experimental-design/test-matrix layer

## Objective

Convert the previously defined metrology test strategy into reproducible Python-generated design tables before any final hidden DUT personality is frozen or any full synthetic validation dataset is generated.

## Previous verified milestones

- `SV-001 — Static Generator Verification`: PASS
- `SV-002 — Dynamic Generator Verification`: PASS

These are historical prerequisites only; this handoff documents the new experimental-design layer.

## Technical work completed

A reusable `src/experiments.py` module now defines the project test matrix through `ExperimentalDesignConfig` and dedicated matrix-builder functions.

Implemented design families:

1. **Static characterization / calibration / validation**
   - RH levels: 20, 30, 40, 50, 60, 70, 80 %RH
   - Temperature levels: 15, 25, 35 °C
   - Directions: Up / Down
   - Days: 1, 2, 3
   - Runs: 2 per day
   - Total: 252 condition-holds
   - Stable hold: 60 s at 1 Hz

2. **Calibration / blind-validation split**
   - Calibration: 20, 40, 60, 80 %RH on Days 1–2
   - Blind validation: 30, 50, 70 %RH on Day 3
   - Remaining static conditions retain the `CHARACTERIZATION` role
   - Analysis roles are mutually exclusive

3. **Dynamic step DOE**
   - 30→70 and 70→30 %RH
   - Temperatures: 15, 25, 35 °C
   - Five repetitions per step/temperature combination
   - Total: 30 tests
   - 60 s baseline + 240 s transient
   - Metrics: dead time, tau, t90, settling time, overshoot

4. **Ramp DOE**
   - 30↔70 %RH
   - 2 %RH/min
   - Three temperatures
   - Three repetitions
   - Total: 18 tests
   - Each 40 %RH ramp lasts 1200 s

5. **Cyclic DOE**
   - 30↔70 %RH at 25 °C
   - Five cycles per session
   - Three sessions

6. **Sinusoidal DOE**
   - Center: 50 %RH
   - Amplitude: 10 %RH
   - Periods: 600, 300, 120, 60 s
   - Metrics: gain and phase lag

7. **Stability / drift schedule**
   - 90-day synthetic aging program
   - Weekly 50 %RH / 25 °C center checks
   - Multi-point checks at Days 30, 60, and 90 using 30/50/70 %RH

8. **Uncertainty evaluation points**
   - 30, 50, 70 %RH at 25 °C
   - 80 %RH at 35 °C as the designated worst-case point

## Verification gate

A new verification script was added under:

`verification/ED-001_Experimental_Design/ed001_experimental_design_verification.py`

The gate checks eleven structural properties:

- ED-001A: full 252-condition static factorial count
- ED-001B: static balance across RH, temperature, direction, day, and run
- ED-001C: expected calibration / validation / characterization counts
- ED-001D: declared calibration and validation holdout logic
- ED-001E: dynamic step DOE count and replication
- ED-001F: ramp DOE count, rate, and duration
- ED-001G: cyclic DOE session/cycle structure
- ED-001H: sinusoidal periods and reciprocal frequencies
- ED-001I: 90-day stability schedule
- ED-001J: uncertainty evaluation points
- ED-001K: globally unique Test_ID values

## Verification result

`ED-001 = PASS (11/11 checks)`

The generated design contains 333 globally unique test IDs across all currently defined test families.

## Repository hygiene

Generated analyst/private verification fixtures and generated ED-001 matrix CSV files are now ignored by `.gitignore` so local execution does not pollute `git status`. Curated verification reports remain tracked.

## Design decision

The experiment matrix is defined before final hidden DUT parameters are frozen. This preserves the intended order:

```text
requirements
-> verified simulator physics
-> predefined experiment design
-> freeze hidden DUT/reference/chamber truth
-> generate raw synthetic measurements
-> analyze without access to hidden truth
```

This prevents test conditions from being tailored after the final synthetic DUT behavior is known.

## Next milestone

Define the final public/private configuration boundary and freeze the hidden DUT/reference/chamber parameter set without exposing final private truth to analyst-facing notebooks or tracked repository data.
