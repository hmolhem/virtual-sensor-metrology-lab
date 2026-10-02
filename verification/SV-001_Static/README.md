# SV-001 Static Generator Verification

SV-001 verifies the static synthetic-data generator before any final project dataset is created.

The verification fixture intentionally uses known truth values so that the simulator equations and stochastic behavior can be checked directly.

## Checks

- deterministic DUT offset
- deterministic reference bias
- quantization behavior
- repeatability-noise statistics
- chamber-stability statistics
- day/run/noise hierarchy
- fixed-seed reproducibility
- private/public field separation

## Result

All eight checks PASS. See `sv001_verification_report.csv`.

## Generated local outputs

Running `sv001_static_verification.py` also generates:

- `sv001_private_truth.csv`
- `sv001_analyst.csv`

These files are reproducible outputs of the fixture and do not need to be treated as authoritative source files in the repository.
