# HO-006 — Laboratory Scope Separation

## Milestone identity

- Project: Synthetic Sensor Metrology Lab
- Historical repository name: `full-sensor-validation-metrology`
- Branch: `refactor/synthetic-metrology-lab-scope`
- Date: 2026-10-01
- Scope: Separate the synthetic laboratory from the future DS 7140 analysis repository

## Objective

Clarify the repository boundary before hidden simulator truth is frozen or the final synthetic dataset is generated.

The current repository is now defined as a **virtual metrology laboratory and dataset-generation system**. The downstream DS 7140 analysis will be created later in a separate repository using only the released analyst-facing measurement package.

## Architectural decision

The project is split into two independent repositories:

```text
Repository A — Synthetic Sensor Metrology Lab
    simulator physics
    chamber / reference / DUT / DAQ
    private hidden truth
    verification gates
    experiment design
    measurement campaign
    analyst-facing dataset release

Repository B — Future DS 7140 Course Project
    released dataset ingestion
    EDA / statistics
    ANOVA / variance components
    calibration
    blind validation
    dynamic characterization
    stability / drift
    uncertainty / Monte Carlo
    compliance decisions
    notebooks / figures / final report
```

Repository B does not exist yet. It will be created only after Repository A produces a frozen release package.

## Changes completed

- Reframed the root README around the **Synthetic Sensor Metrology Lab** scope.
- Updated the architecture document so the laboratory boundary ends at dataset release.
- Added `docs/02_LAB_TO_DS7140_INTERFACE.md` defining the formal information contract between the two repositories.
- Added `data/generated/README.md` for versioned analyst-facing dataset releases.
- Reclassified `data/raw/` as internal laboratory staging rather than a course-analysis data area.
- Removed empty downstream-analysis placeholders for:
  - `notebooks/`
  - `results/`
  - `report/`
  - `data/calibration/`
  - `data/processed/`
  - `data/validation/`
  - legacy `data/dynamic/`
- Updated the simulator package description in `src/__init__.py`.
- Preserved all simulator source code, verification gates, experimental-design code, and historical handoffs.

## Public/private boundary principle

The laboratory release may expose measurements, public specifications, test metadata, timestamps, setpoints, and dataset provenance.

The initial DS 7140 repository must not receive exact hidden DUT/reference/chamber parameters, latent true environmental states, or injected error components.

A post-analysis truth audit may be performed only after the downstream analysis is frozen.

## Verification / consistency review

This milestone changes repository scope and documentation, not simulator physics.

Consistency checks:

- existing `SV-001`, `SV-002`, and `ED-001` verification artifacts remain intact;
- simulator source files remain in the laboratory repository;
- downstream analysis placeholders are removed;
- a dedicated dataset-release path now exists;
- the lab-to-course interface explicitly protects hidden truth;
- history, handoff, and index continuity remain intact.

## Repository rename

Recommended repository name:

`synthetic-sensor-metrology-lab`

The connected GitHub tooling available during this milestone does not expose repository-settings rename capability. Therefore the repository content and scope are fully migrated first; the GitHub repository-name change must be performed separately through repository settings when convenient.

## Next technical milestone

Define and verify the public/private configuration boundary, then freeze the final hidden DUT/reference/chamber parameter set before running the final synthetic measurement campaign.
