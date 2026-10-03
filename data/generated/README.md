# Generated Dataset Releases

This directory is the formal boundary for **analyst-facing synthetic measurement releases** produced by the verified Virtual Sensor Metrology Lab.

Only public measurement data and public metadata belong here. Private simulator truth, latent states, exact hidden parameters, injected error components, and private configuration files must never be included in this release path.

## Release-candidate contents

The first release candidate, `VSM-LAB-DATA-v1`, contains:

- `static_measurements.csv`
- `dynamic_step_measurements.csv`
- `ramp_measurements.csv`
- `cyclic_measurements.csv`
- `sinusoidal_measurements.csv`
- `stability_measurements.csv`
- `test_matrix.csv`
- `dataset_manifest.json`

The simulator-only counterpart remains under `data/private_truth/` and is excluded from the analyst release.

## Freeze rule

Generation alone does **not** make a dataset frozen.

A release becomes eligible for freeze only after the on-disk release candidate passes:

```text
verification/DR-001_Dataset_Release/dr001_dataset_release_verification.py
```

`DR-001` verifies:

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

Only after `DR-001 = PASS` may `VSM-LAB-DATA-v1` be recorded as the first frozen analyst-facing release and handed to the separate DS 7140 analysis repository.
