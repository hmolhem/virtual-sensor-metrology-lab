# HO-002 — SV-002 Dynamic Generator Verification

## Milestone identity

- Project: Full Sensor Validation & Metrology
- Branch: `feature/sv002-dynamic-verification`
- Date: 2026-10-01
- Scope: Verification of the dynamic synthetic-data engine using a known first-order sensor fixture

## Objective

Verify that the dynamic simulation engine reproduces known first-order behavior, dead time, rise/fall asymmetry, sampled threshold timing, cascaded chamber/reference/DUT dynamics, fixed-seed reproducibility, and public/private data separation before the final hidden DUT is frozen.

## Known verification fixture

The dynamic verification fixture intentionally uses known truth:

- RH step: 30 -> 70 %RH
- DUT time constant: 20 s
- DUT dead time: 3 s
- Chamber time constant for the cascaded test: 30 s
- Reference time constant for the cascaded test: 4 s
- Default sampling interval: 1 s
- Fine sampling check: 0.25 s
- Master random seed: 7140

This fixture is not the final project sensor. Its purpose is simulator verification against analytical expectations.

## Work completed

1. Added a continuous first-order analytical step-response model with optional pure dead time.
2. Added exact zero-order-hold first-order discrete dynamics for sampled simulation.
3. Added threshold-based t90 estimation for rising and falling responses.
4. Added a log-linear estimator for recovering tau from a clean isolated first-order trace.
5. Added a dynamic chain simulator for command -> chamber -> reference/DUT.
6. Added independent random streams for reference and DUT measurement noise.
7. Added public analyst and private verification data views.
8. Added ten explicit verification checks and a machine-readable PASS report.

## SV-002 verification results

| Test | Purpose | Result |
|---|---|---|
| SV-002A | Verify 63.2% response at one time constant | PASS |
| SV-002B | Verify analytical t90 relation | PASS |
| SV-002C | Verify dead-time shift of observed t90 | PASS |
| SV-002D | Recover the known DUT tau with the log-linear estimator | PASS |
| SV-002E | Verify 1 Hz threshold-timing discretization bound | PASS |
| SV-002F | Verify rise/fall asymmetry under unequal time constants | PASS |
| SV-002G | Verify cascaded chamber/reference/DUT convergence | PASS |
| SV-002H | Verify fixed-seed reproducibility | PASS |
| SV-002I | Verify dynamic public/private field separation | PASS |
| SV-002J | Verify that finer sampling does not worsen threshold timing | PASS |

## Key numerical checks

For tau = 20 s:

- 63.2% level for a 30 -> 70 %RH step: 55.28482235 %RH
- intrinsic t90: 46.05170186 s
- observed t90 with 3 s pure dead time: 49.05170186 s
- recovered tau from the clean trace: 20.00000000 s
- first 1 Hz sampled threshold crossing: 50.000 s
- 1 Hz threshold discretization error: 0.9483 s
- 4 Hz threshold discretization error: 0.1983 s

The cascaded 240 s simulation converged close to the 70 %RH final command:

- chamber: 69.9813 %RH
- reference dynamic state: 69.9780 %RH
- DUT dynamic state: 69.9378 %RH

## Key design decisions

- The verification fixture uses known truth and may expose internal states because its purpose is to test the simulator itself.
- Final hidden DUT truth remains separate and must not be committed.
- Dynamic sensor analysis must distinguish intrinsic DUT response from chamber dynamics, reference dynamics, and DAQ sampling effects.
- Threshold-based t90 is sampling-resolution dependent; model-based parameter estimation is treated as a distinct method.
- Rise and fall dynamics are allowed to use different time constants in the final simulator.

## Gate decision

`SV-002 = PASS`

The static and dynamic simulator foundations have now both passed their initial verification gates:

- `SV-001 = PASS`
- `SV-002 = PASS`

This is sufficient to proceed to the next architectural milestone: refactoring verified simulation logic into reusable source modules before freezing the final hidden DUT personality.

## Next milestone

Refactor the verified static and dynamic simulation logic into reusable modules under `src/`, preserving all existing verification behavior. This work must be performed on a new task branch after this pull request is merged.
