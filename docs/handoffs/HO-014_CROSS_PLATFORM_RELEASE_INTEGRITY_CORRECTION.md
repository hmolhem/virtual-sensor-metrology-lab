# HO-014 — Cross-Platform Release Integrity Correction

**Date:** 2026-10-03  
**Branch:** `release/vsm-lab-data-v1-1-integrity-correction`  
**Repository:** `hmolhem/virtual-sensor-metrology-lab`

## Objective

Correct a cross-platform line-ending defect in the release-provenance chain without changing the synthetic measurement payload.

The corrective analyst-facing release is:

```text
VSM-LAB-DATA-v1.1
```

## Trigger

During downstream frozen-dataset intake, SHA-256 verification exposed a discrepancy between the historical `VSM-LAB-DATA-v1` release commitment and the Git-committed `dataset_manifest.json` bytes.

The historical commitment recorded this manifest SHA-256:

```text
8a24322f883f2bc3c42f870072e7f75b9ac8087492a7fa8c339e51ea9092c146
```

However, the manifest stored in Git at the historical dataset commit was canonical LF text with SHA-256:

```text
b15fa4a4a33e91fd0b8478b3c763412cdc8db6a104e5ae0d5ff9e081465aec2e
```

The discrepancy was traced to Windows Git line-ending conversion:

```text
core.autocrlf = true
index: LF
working tree: CRLF
```

The original freeze procedure hashed the Windows working-tree manifest before Git normalized it to LF on commit. Git therefore considered the repository clean while byte-level SHA-256 differed across the working tree and committed artifact.

## Root-cause confirmation

The historical manifest blob was extracted directly from commit:

```text
ab00064fb3b3f56014a6d4f7084a339de9254b9b
```

The same manifest content produced:

```text
LF SHA-256   = b15fa4a4a33e91fd0b8478b3c763412cdc8db6a104e5ae0d5ff9e081465aec2e
CRLF SHA-256 = 8a24322f883f2bc3c42f870072e7f75b9ac8087492a7fa8c339e51ea9092c146
```

This established that the defect was release packaging/provenance, not measurement-data corruption.

## Corrective-release policy

`VSM-LAB-DATA-v1` remains historically frozen and is not rewritten in place.

A new corrective release was created:

```text
VSM-LAB-DATA-v1.1
```

The correction is restricted to:

1. canonical LF line-ending policy;
2. corrected release identity;
3. corrected manifest commitment;
4. explicit cross-platform release-integrity verification.

The seven CSV payload commitments are unchanged from `VSM-LAB-DATA-v1`.

## Canonical line-ending policy

A repository-level `.gitattributes` file now enforces LF for analyst-facing release artifacts and verification CSV evidence:

```text
data/generated/*.csv text eol=lf
data/generated/*.json text eol=lf
data/generated/README.md text eol=lf
verification/**/*.csv text eol=lf
```

This prevents platform-dependent CRLF/LF conversion from changing future byte-level release commitments.

## Corrective release identity

The v1.1 manifest identifies:

```text
release_id = VSM-LAB-DATA-v1.1
```

Its canonical committed SHA-256 is:

```text
efd9e79958b9d7c7b8730ee9015c72c3e8205effd03c686ff58b03454188f847
```

The corrective release commitment is recorded at:

```text
data/generated/release_commitment_v1_1.json
```

and links back to:

```text
parent_release_id = VSM-LAB-DATA-v1
parent_dataset_commit_sha = ab00064fb3b3f56014a6d4f7084a339de9254b9b
measurement_payload_changed = false
```

## DR-002 verification gate

A dedicated cross-platform gate was added at:

```text
verification/DR-002_Cross_Platform_Release_Integrity/dr002_cross_platform_release_integrity.py
```

Final execution result:

```text
DR-002 = PASS (11/11)
```

DR-002 verified:

1. corrective release identity and parent linkage;
2. required canonical-LF `.gitattributes` policy;
3. committed v1.1 manifest SHA-256 against the release commitment;
4. all seven committed CSV payload hashes against the manifest;
5. unchanged CSV commitments relative to historical v1;
6. manifest semantic change limited to the release identifier;
7. canonical LF with no CR bytes in committed release artifacts;
8. row counts and schemas against the manifest;
9. preservation of the analyst/private-truth boundary and hidden-personality commitment;
10. absence of tracked private simulator-truth files in the release directory;
11. final frozen corrective-release metadata state.

The final verification evidence is tracked at:

```text
verification/DR-002_Cross_Platform_Release_Integrity/dr002_verification_report.csv
```

## Measurement payload preservation

The following measurement and design artifacts retain the same SHA-256 commitments as historical v1:

- `static_measurements.csv`
- `dynamic_step_measurements.csv`
- `ramp_measurements.csv`
- `cyclic_measurements.csv`
- `sinusoidal_measurements.csv`
- `stability_measurements.csv`
- `test_matrix.csv`

No DUT/reference/chamber measurement values were regenerated or altered as part of HO-014.

## Information boundary

The corrective release preserves the same analyst/private boundary as v1. No exact hidden DUT/reference/chamber parameters, latent simulator states, injected error components, or private truth files are included in the analyst-facing release.

## Final release status

```text
VSM-LAB-DATA-v1.1 = FROZEN
DR-002 = PASS (11/11)
measurement_payload_changed = false
```

`VSM-LAB-DATA-v1.1` is the canonical corrective analyst-facing release for downstream intake.

## Engineering lesson

Git content equivalence and release-artifact byte identity are not the same thing when line-ending conversion is active. A clean Git working tree does not guarantee that a locally hashed text artifact is byte-identical to the committed blob.

Future release commitments must therefore be derived from canonical committed bytes, with line endings explicitly controlled by `.gitattributes` and cross-platform integrity verified before release freeze.
