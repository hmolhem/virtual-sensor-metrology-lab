# Generated Dataset Releases

This directory is the formal boundary for **analyst-facing synthetic measurement releases** produced by the verified Virtual Sensor Metrology Lab.

Only public measurement data and public metadata belong here. Private simulator truth, latent states, exact hidden parameters, injected error components, and private configuration files must never be included in this release path.

## Frozen release

The first frozen analyst-facing release is:

```text
VSM-LAB-DATA-v1
```

It contains:

- `static_measurements.csv`
- `dynamic_step_measurements.csv`
- `ramp_measurements.csv`
- `cyclic_measurements.csv`
- `sinusoidal_measurements.csv`
- `stability_measurements.csv`
- `test_matrix.csv`
- `dataset_manifest.json`
- `release_commitment_v1.json`

The simulator-only counterpart remains under `data/private_truth/` and is excluded from the analyst release.

## Freeze verification

The actual on-disk release passed:

```text
DR-001 = PASS (10/10)
```

using:

```text
verification/DR-001_Dataset_Release/dr001_dataset_release_verification.py
```

`DR-001` verified:

1. all required analyst-facing files exist;
2. release identity and hidden-personality commitment match;
3. on-disk CSV SHA-256 hashes match `dataset_manifest.json`;
4. row counts match the approved campaign design;
5. unique Test-ID counts match the experimental design;
6. analyst-facing schemas contain no hidden-truth fields;
7. DUT/reference quantization is preserved;
8. released measurements are finite and physically bounded;
9. no private simulator-truth files are present in `data/generated/`;
10. manifest row metadata agrees with the actual files.

## Release commitment

Dataset-manifest SHA-256:

```text
8a24322f883f2bc3c42f870072e7f75b9ac8087492a7fa8c339e51ea9092c146
```

The authoritative freeze metadata is recorded in:

```text
release_commitment_v1.json
```

## Immutability rule

`VSM-LAB-DATA-v1` is frozen and immutable by project policy.

Any change to analyst-facing release content, manifest contents, or release identity requires a new release ID and a fresh release-verification/freeze cycle.
