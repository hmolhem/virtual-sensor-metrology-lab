# SV-002 — Dynamic Generator Verification

## Purpose

Verify the dynamic synthetic-data engine before any final hidden DUT is frozen or any full project dataset is generated.

The verification fixture uses known parameters so analytical expectations can be compared directly with generated results.

## Known fixture

- Step: 30 -> 70 %RH
- Isolated DUT time constant: 20 s
- DUT dead time: 3 s
- Chamber time constant in cascaded test: 30 s
- Reference time constant in cascaded test: 4 s
- Sampling interval: 1 s unless otherwise noted
- Master seed: 7140

## Verification checks

| Test | Check |
|---|---|
| SV-002A | 63.2% first-order property at t = tau |
| SV-002B | t90 = -tau ln(0.1) = 2.302585 tau |
| SV-002C | pure dead time shifts observed t90 |
| SV-002D | known tau recovered by log-linear estimator |
| SV-002E | 1 Hz threshold-time discretization bound |
| SV-002F | rise/fall asymmetry behaves consistently with different tau values |
| SV-002G | chamber/reference/DUT cascade converges to final command |
| SV-002H | fixed-seed reproducibility |
| SV-002I | analyst/private dynamic-field separation |
| SV-002J | finer sampling reduces or preserves threshold timing accuracy |

## Result

All ten checks PASS.

## Important distinction

This is a **simulator verification fixture**, not the final sensor-validation dataset. Known truth is intentionally used here so the dynamic engine can be checked against analytical physics.

The script can generate local fixture CSV files for private and analyst views. These are verification artifacts only and are not the final hidden project truth.
