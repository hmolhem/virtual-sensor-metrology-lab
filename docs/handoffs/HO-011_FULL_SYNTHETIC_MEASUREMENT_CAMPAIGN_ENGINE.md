# HO-011 — Full Synthetic Measurement Campaign Engine

## Branch

`feature/full-synthetic-measurement-campaign`

## Date

2026-10-03

## Objective

Implement the executable full synthetic measurement campaign that converts the verified experimental design and frozen hidden laboratory personality into analyst-facing measurement datasets while preserving a strict private-truth boundary.

## Scope

This milestone adds the campaign-generation layer only. It does **not** yet freeze the final analyst-facing dataset release in Git.

The campaign engine covers:

- static 7 RH × 3 temperature × 2 direction × 3 day × 2 run design
- dynamic step tests
- dynamic ramp tests
- cyclic tracking tests
- sinusoidal frequency-response tests
- 90-day stability/drift checks
- separate simulator-only truth products
- deterministic RNG streams derived from the frozen private master seed
- analyst-schema leakage protection
- release-manifest hashing support

## Public execution protocol

Added:

`config/public/campaign_execution_v1.json`

This records campaign details that were not fully specified by the higher-level experimental design, including cyclic half-cycle duration, sinusoidal cycles per period, stability hold duration, serialization format, and release identity.

## Campaign engine

Added:

`src/campaign.py`

The engine:

1. loads the public configuration and sealed private personality;
2. verifies the private SHA-256 commitment before generation;
3. applies chamber, reference, DUT, DAQ, static-error, dynamic-response, hysteresis, drift, and hierarchical random-effect behavior;
4. generates analyst-facing and private-truth products separately;
5. blocks simulator-only columns from analyst-facing outputs;
6. writes deterministic CSV products and a SHA-256 dataset manifest.

The earlier SV-001/SV-002 verification fixtures remain unchanged. The campaign engine is a production measurement-campaign layer, not a replacement for those fixtures.

## MC-001 verification

Added:

`verification/MC-001_Full_Campaign/mc001_full_campaign_verification.py`

Verification outcome:

`MC-001 = PASS (8/8)`

Verified properties:

- frozen personality commitment matches;
- analyst row counts match the campaign design;
- unique Test_ID counts match the experimental design;
- analyst schemas contain no hidden-truth fields;
- repeated generation is deterministic;
- private products retain simulator truth separately;
- DUT/reference quantization is preserved;
- generated RH outputs are finite and physically bounded.

Expected analyst row counts:

- static: 15,120 rows / 252 tests
- dynamic step: 9,030 rows / 30 tests
- ramp: 21,618 rows / 18 tests
- cyclic: 9,003 rows / 3 sessions
- sinusoidal: 5,404 rows / 4 periods
- stability: 1,320 rows / 22 checks

## Information boundary

No exact hidden DUT/reference/chamber parameters were committed.

Final private input remains local under:

`config/private/final_lab_personality_v1.json`

Simulator-only campaign products are written under:

`data/private_truth/`

Analyst-facing products are written under:

`data/generated/`

## Outcome

The virtual laboratory now has an executable, deterministic, leakage-checked full measurement-campaign engine driven by the frozen laboratory personality.

## Next milestone

Run the campaign in the user's local DS environment, inspect the generated analyst-facing files and manifest, rerun `MC-001`, then freeze the first analyst-facing dataset release as a separate milestone.
