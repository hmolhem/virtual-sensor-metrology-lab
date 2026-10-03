# HO-008 — Public / Private Configuration Boundary

## Milestone identity

- Project: Virtual Sensor Metrology Lab
- Branch: `feature/public-private-config-boundary`
- Verification gate: `CB-001`
- Status: Complete
- Date: 2026-10-03

## Purpose

Formalize the information boundary between analyst-visible laboratory specification and simulator-only hidden truth before final DUT/reference/chamber truth is frozen.

This milestone deliberately does **not** define the final hidden sensor personality. It creates the protected interface that must exist before those values are chosen.

## Technical changes

### Public configuration

Added:

`config/public/lab_spec_v1.json`

The file contains only declared analyst-visible information:

- laboratory identity and measurand
- DUT operating range, resolution, and acceptance limits
- reference-instrument public specification
- chamber public specification
- DAQ/sampling specification
- static and dynamic experimental-design metadata
- stability schedule and uncertainty-evaluation points

It contains no final hidden DUT/reference/chamber parameters.

### Executable information boundary

Added:

`src/config_boundary.py`

The module provides:

- `load_public_config()`
- `load_private_truth()`
- `find_private_keys()`
- `assert_analyst_payload_safe()`
- `write_analyst_json()`
- `ConfigurationBoundaryError`

The private loader fails closed unless simulator truth is located under `config/private/`.

The analyst-output gate rejects explicit truth/hidden/latent/private fields and known hidden-parameter field names such as exact offset/bias, dynamic tau, dead time, drift, and random-effect terms.

### Git protection

Existing protection was retained:

- `config/private/*`
- `data/private_truth/*`

Only the tracked policy READMEs remain exempt.

CB-001 temporary fixtures were also added to `.gitignore` so verification does not leave private dummy truth or analyst-output scratch files in the working tree.

### Policy documentation

Updated:

- `config/README.md`
- `config/private/README.md`
- `data/private_truth/README.md`
- `src/README.md`
- root `README.md`

The project front page now records CB-001 as complete and identifies hidden-truth freeze as the next engineering milestone.

## CB-001 verification

Added:

`verification/CB-001_Config_Boundary/cb001_config_boundary_verification.py`

and the curated result:

`verification/CB-001_Config_Boundary/cb001_verification_report.csv`

Checks:

- A — public configuration loads with required sections
- B — DUT public acceptance limits are complete
- C — public configuration contains no private fields
- D — protected private fixture loads successfully
- E — private truth outside `config/private/` is rejected
- F — canonical analyst record passes the boundary gate
- G — leaked private fields are rejected
- H — analyst JSON serialization enforces the boundary
- I — `.gitignore` contains required private-path protections
- J — no actual private truth files are tracked
- K — public experimental role policy matches the declared design split

Result:

`CB-001 = PASS (11/11)`

A separate execution mirror of the branch logic was used to exercise the verification script before recording the curated result; repository contents were also inspected to confirm that only the two policy README files are tracked under the protected private paths.

## Scientific / metrology significance

The project now has an explicit separation between:

```text
PUBLIC / ANALYST-VISIBLE
specifications + test design + measured channels + release metadata
```

and:

```text
PRIVATE / SIMULATOR-ONLY
exact hidden DUT/reference/chamber behavior + latent states + injected errors
```

This prevents the downstream DS 7140 analysis from becoming circular or artificially easy by exposing the exact model that generated the measurements.

## What did not change

This milestone does not alter:

- SV-001 verified static simulator behavior
- SV-002 verified dynamic simulator behavior
- ED-001 experimental-design counts or role split
- final hidden DUT/reference/chamber values, because they are still unfrozen
- any final analyst-facing dataset, because the measurement campaign has not yet been run

## Next milestone

Freeze the final hidden laboratory personality locally/private:

- DUT static error structure
- DUT dynamic parameters
- hysteresis and drift behavior
- day/run random effects
- reference hidden bias/error behavior
- chamber hidden bias/nonuniformity/dynamics
- RNG seed/commitment strategy

After that hidden configuration is frozen and independently sanity-checked, the full synthetic measurement campaign can be generated.
