# HO-013 — Dataset Release v1 Freeze

**Date:** 2026-10-03  
**Branch:** `release/finalize-vsm-lab-data-v1`  
**Repository:** `hmolhem/virtual-sensor-metrology-lab`

## Objective

Formally freeze the first analyst-facing synthetic dataset release produced by the Virtual Sensor Metrology Lab.

The release identifier is:

```text
VSM-LAB-DATA-v1
```

## Preconditions satisfied

The release was frozen only after the following conditions were satisfied:

1. the full synthetic measurement campaign was generated locally from the sealed hidden personality;
2. `MC-001 = PASS (8/8)` verified the campaign generator behavior;
3. `DR-001 = PASS (10/10)` verified the actual on-disk release candidate;
4. the release files were committed on the dedicated release branch;
5. the dataset manifest was cryptographically fingerprinted and recorded.

## Frozen release contents

The analyst-facing release contains:

- `data/generated/static_measurements.csv`
- `data/generated/dynamic_step_measurements.csv`
- `data/generated/ramp_measurements.csv`
- `data/generated/cyclic_measurements.csv`
- `data/generated/sinusoidal_measurements.csv`
- `data/generated/stability_measurements.csv`
- `data/generated/test_matrix.csv`
- `data/generated/dataset_manifest.json`
- `data/generated/release_commitment_v1.json`

The corresponding DR-001 evidence is tracked at:

```text
verification/DR-001_Dataset_Release/dr001_verification_report.csv
```

## Release identity

Dataset manifest SHA-256:

```text
8a24322f883f2bc3c42f870072e7f75b9ac8087492a7fa8c339e51ea9092c146
```

Dataset commit SHA:

```text
ab00064fb3b3f56014a6d4f7084a339de9254b9b
```

The release is linked to the sealed hidden laboratory personality:

```text
VSM-LAB-HP-v1
```

with hidden-personality SHA-256 commitment:

```text
e534c04fb3718b4ae1dfe911c369bde3e1c37d922aaffeaa66bf400ebdbc1998
```

## Verification status

```text
MC-001 = PASS (8/8)
DR-001 = PASS (10/10)
```

DR-001 verified the actual files on disk for:

- required-file presence;
- release identity;
- manifest hash integrity;
- row counts;
- unique test counts;
- analyst/private schema separation;
- quantization preservation;
- finite and physically bounded measurements;
- private-truth exclusion;
- manifest metadata consistency.

## Release dimensions

- static measurements: 15,120 rows / 252 tests
- dynamic step measurements: 9,030 rows / 30 tests
- ramp measurements: 21,618 rows / 18 tests
- cyclic measurements: 9,003 rows / 3 sessions
- sinusoidal measurements: 5,404 rows / 4 periods
- stability measurements: 1,320 rows / 22 checks
- combined test matrix: 333 rows

## Information boundary

No exact hidden DUT/reference/chamber parameters, latent physical states, injected error components, or private truth files are included in the analyst-facing release.

Private simulator products remain under protected local paths and are not part of the dataset handoff.

## Freeze rule

`VSM-LAB-DATA-v1` is now immutable by policy.

Any modification to analyst-facing CSV content, `dataset_manifest.json`, release identity, or release provenance requires:

1. a new release ID;
2. regeneration or explicit transformation under a new release milestone;
3. a new manifest commitment;
4. a fresh DR-001-equivalent on-disk verification.

## Outcome

The first analyst-facing dataset release is formally frozen and is now eligible to become the input boundary for the separate DS 7140 analysis repository.

The next project phase is no longer virtual-lab construction. The next phase is downstream analysis of this frozen release without access to the exact hidden simulator truth.
