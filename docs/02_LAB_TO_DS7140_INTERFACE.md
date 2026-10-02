# Laboratory-to-DS7140 Interface

## Purpose

This document defines the formal boundary between the **Synthetic Sensor Metrology Lab** repository and the future **DS 7140 course-project** repository.

The lab repository creates and verifies the synthetic measurement system. The DS 7140 repository begins only after the lab produces a frozen analyst-facing dataset release.

## Ownership split

### Synthetic Sensor Metrology Lab owns

- chamber, reference, DUT, and DAQ models
- hidden simulator truth
- simulator verification
- experimental design and measurement scheduling
- synthetic measurement generation
- release packaging
- release provenance and public metadata

### DS 7140 course project owns

- data ingestion and cleaning
- exploratory data analysis
- descriptive statistics
- repeatability/reproducibility analysis
- ANOVA and variance components
- calibration model fitting
- blind validation
- dynamic parameter estimation from released measurements
- stability/drift analysis
- uncertainty budget
- Monte Carlo uncertainty propagation
- compliance decisions
- notebooks, figures, tables, and final report

## Analyst-facing release package

The lab will release a versioned package containing measurement files and public metadata only. The expected structure is:

```text
data/generated/
    static_measurements.csv
    dynamic_step_measurements.csv
    ramp_measurements.csv
    cyclic_measurements.csv
    sinusoidal_measurements.csv
    stability_measurements.csv
    test_matrix.csv
    dataset_manifest.json
    README.md
```

The exact filenames may evolve before the first frozen release, but the information boundary must not.

## Public information allowed in the DS 7140 repository

The downstream repository may receive:

- analyst-facing measurement channels
- timestamps
- Test_ID / Run_ID / Day_ID
- declared chamber setpoints and logged conditions
- declared DUT specification / acceptance criteria
- declared reference-instrument specification
- declared chamber specification
- sampling and DAQ metadata
- test-matrix metadata
- dataset version, generation date, and provenance

## Information forbidden from the initial DS 7140 dataset

The downstream repository must not initially receive:

- exact hidden DUT offset
- exact hidden gain/sensitivity error
- exact hidden nonlinearity coefficients
- exact hidden temperature coefficients or interaction terms
- exact hidden hysteresis law
- exact hidden drift law
- exact hidden dynamic tau/dead-time parameters
- exact hidden day/run random-effect values
- exact hidden reference bias/error parameters
- exact hidden chamber bias/nonuniformity parameters
- latent true RH or temperature states
- injected per-sample error components

These values remain private to the simulator so the downstream analysis is genuinely blind.

## Optional final truth audit

After the full DS 7140 analysis is complete and frozen, a separate audit may compare analyst estimates with the sealed simulator truth.

That audit is explicitly **post-analysis**. It must not influence model selection, calibration fitting, uncertainty construction, or validation decisions.

## Release rule

A dataset is not considered ready for transfer until all of the following are true:

1. static simulator verification passes;
2. dynamic simulator verification passes;
3. experimental-design verification passes;
4. public/private configuration boundary passes its verification gate;
5. final hidden DUT/reference/chamber truth is frozen;
6. the complete measurement campaign is generated reproducibly;
7. analyst-facing files contain no forbidden private-truth fields;
8. a versioned dataset manifest records provenance and checksums.

## Repository transition

When the first frozen dataset release is ready, create a separate DS 7140 repository from that release package. Do not clone or copy simulator internals into the course repository.
