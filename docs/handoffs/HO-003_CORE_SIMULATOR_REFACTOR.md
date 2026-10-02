# HO-003 — Core Simulator Refactor

## Milestone identity

- Project: Full Sensor Validation & Metrology
- Branch: `refactor/core-simulator-modules`
- Date: 2026-10-01
- Scope: Refactor verified static and dynamic simulation logic into reusable core modules

## Previous verified milestones

- `SV-001 — Static Generator Verification`: PASS
- `SV-002 — Dynamic Generator Verification`: PASS

These two gates are historical prerequisites for this refactor and remain the reference behavior that the reusable core must preserve.

## Objective

Move simulator behavior out of standalone verification scripts and into reusable `src/` modules without changing the verified numerical behavior.

## Technical work completed

1. Added `src/chamber.py` for chamber static behavior and commanded-step generation.
2. Added `src/reference.py` for the reference-instrument static model.
3. Added `src/dut.py` for the DUT static model.
4. Added `src/daq.py` for static and dynamic acquisition timebases.
5. Added `src/dynamics.py` for analytical and discrete first-order dynamic response utilities and parameter estimators.
6. Added `src/utils.py` for quantization and independent random-number streams.
7. Added `src/simulation.py` to orchestrate static datasets, hierarchical fixtures, and the chamber/reference/DUT dynamic chain.
8. Added `src/__init__.py` and updated `src/README.md` to define the reusable simulator package.
9. Refactored the SV-001 and SV-002 verification scripts so they import and exercise the reusable core instead of maintaining duplicate simulator implementations.

## Verification performed

Both refactored verification scripts were executed against the reusable core.

### SV-001 result

All eight checks passed:

- deterministic DUT offset
- deterministic reference bias
- quantization
- repeatability-noise statistics
- chamber-stability statistics
- hierarchical day/run/random-noise behavior
- fixed-seed reproducibility
- analyst/private-data separation

Overall result: `PASS`.

### SV-002 result

All ten checks passed:

- 63.2% first-order property
- analytical t90 relation
- dead-time shift
- tau recovery
- sampled threshold timing
- rise/fall asymmetry
- cascaded convergence
- fixed-seed reproducibility
- analyst/private-data separation
- sampling-resolution behavior

Overall result: `PASS`.

## Engineering decision

Verification scripts are now consumers of the same simulator core that future experiment generators will use. This reduces implementation drift and establishes one authoritative path for future static and dynamic data generation.

No final hidden DUT personality has been frozen in this milestone.

## Next milestone

Define and implement the full experimental-design layer and final hidden DUT/reference/chamber configuration only after agreeing on the test matrix and private/public configuration boundary.
