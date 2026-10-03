# HO-012 — Dataset Release Freeze Gate

**Date:** 2026-10-03  
**Branch:** `release/freeze-dataset-v1`  
**Repository:** `hmolhem/virtual-sensor-metrology-lab`

## Objective

Implement the final on-disk release-verification gate required before the first analyst-facing dataset can be formally frozen.

This milestone does **not** claim that `VSM-LAB-DATA-v1` is already frozen. It establishes the verification procedure that must be run against the actual files generated on the user's local system.

## Context

The production campaign engine is already verified by `MC-001 = PASS (8/8)`, and the user has successfully generated the full campaign locally:

- static measurements: 15,120 rows
- dynamic step measurements: 9,030 rows
- ramp measurements: 21,618 rows
- cyclic measurements: 9,003 rows
- sinusoidal measurements: 5,404 rows
- stability measurements: 1,320 rows
- combined test matrix: 333 rows

Generation alone is not sufficient for a frozen release. The actual on-disk files must be checked against their manifest and the analyst/private boundary.

## Changes

### 1. DR-001 on-disk release verification

Added:

```text
verification/DR-001_Dataset_Release/dr001_dataset_release_verification.py
```

The gate verifies:

1. all required analyst-facing release files exist;
2. release ID and frozen hidden-personality commitment match;
3. on-disk CSV SHA-256 hashes match `dataset_manifest.json`;
4. row counts match the approved campaign design;
5. unique Test-ID counts match the experimental design;
6. analyst-facing schemas contain no hidden-truth fields;
7. static DUT/reference quantization is preserved;
8. released measurements are finite and physically bounded;
9. no private simulator-truth files are present in `data/generated/`;
10. manifest row metadata matches the actual files.

A successful run reports:

```text
DR-001: 10/10 checks PASS
Release candidate VSM-LAB-DATA-v1 is eligible for freeze.
```

### 2. FutureWarning cleanup

Updated `MC-001` to replace deprecated `DataFrame.applymap` usage with `DataFrame.map`.

This is a compatibility cleanup only and does not change the verification criterion or campaign data.

### 3. Release-boundary documentation

Updated `data/generated/README.md` to define:

- the exact release-candidate file set;
- the analyst/private data boundary;
- the DR-001 freeze requirement;
- the rule that generation alone does not constitute a frozen release.

## Verification status

The DR-001 implementation is now ready for local execution against the already-generated `data/generated/` files.

The actual release-freeze gate cannot be marked PASS from GitHub alone because the release candidate currently exists on the user's local working copy and is intentionally not assumed to be identical without on-disk verification.

## Release rule

`VSM-LAB-DATA-v1` may be declared frozen only after the user runs:

```powershell
python verification\DR-001_Dataset_Release\dr001_dataset_release_verification.py
```

and obtains:

```text
DR-001: 10/10 checks PASS
```

## Outcome

The repository now has a formal, reproducible, on-disk dataset-release verification gate.

The next milestone will be **HO-013 — Dataset Release v1 Freeze**, which will record the successful DR-001 result and finalize the first analyst-facing release for transfer into the separate DS 7140 analysis repository.
