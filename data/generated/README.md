# Generated Dataset Releases

This directory is the formal boundary for **analyst-facing synthetic measurement releases** produced by the verified Virtual Sensor Metrology Lab.

Only public measurement data and public metadata belong here. Private simulator truth, latent states, exact hidden parameters, injected error components, and private configuration files must never be included in this release path.

## Canonical frozen release

The canonical analyst-facing release is:

```text
VSM-LAB-DATA-v1.1
```

This is a corrective release of the historical `VSM-LAB-DATA-v1` package. The correction addresses cross-platform line-ending/provenance integrity only; the seven measurement/design CSV payload commitments, schemas, row counts, and hidden-personality commitment are unchanged from v1.

It contains:

- `static_measurements.csv`
- `dynamic_step_measurements.csv`
- `ramp_measurements.csv`
- `cyclic_measurements.csv`
- `sinusoidal_measurements.csv`
- `stability_measurements.csv`
- `test_matrix.csv`
- `dataset_manifest.json`
- `release_commitment_v1_1.json`

The simulator-only counterpart remains under `data/private_truth/` and is excluded from the analyst release.

## Historical release note

`VSM-LAB-DATA-v1` remains historically frozen. During downstream intake, its recorded manifest SHA-256 was found to correspond to CRLF working-tree bytes, while Git stored the manifest with LF line endings. The measurement payload itself was not corrupted or changed.

HO-014 introduced canonical LF policy and the corrective `VSM-LAB-DATA-v1.1` release rather than rewriting v1 in place.

## Freeze verification

The canonical corrective release passed:

```text
DR-002 = PASS (11/11)
```

using:

```text
verification/DR-002_Cross_Platform_Release_Integrity/dr002_cross_platform_release_integrity.py
```

DR-002 verifies release identity and parent linkage, canonical LF policy, committed manifest SHA-256, CSV payload hashes, payload preservation relative to v1, manifest semantic scope, committed line endings, row/schema integrity, analyst/private separation, private-file exclusion, and final frozen commitment state.

The final evidence is tracked at:

```text
verification/DR-002_Cross_Platform_Release_Integrity/dr002_verification_report.csv
```

## Release commitment

Canonical v1.1 dataset-manifest SHA-256:

```text
efd9e79958b9d7c7b8730ee9015c72c3e8205effd03c686ff58b03454188f847
```

The authoritative corrective-release metadata is recorded in:

```text
release_commitment_v1_1.json
```

The historical v1 commitment remains in `release_commitment_v1.json` for provenance.

## Canonical line endings

Repository `.gitattributes` rules enforce LF for analyst-facing CSV/JSON release artifacts and verification evidence so byte-level SHA-256 commitments remain reproducible across platforms.

## Immutability rule

`VSM-LAB-DATA-v1.1` is frozen and immutable by project policy.

Any change to analyst-facing release content, manifest contents, or release identity requires a new release ID and a fresh release-verification/freeze cycle.
