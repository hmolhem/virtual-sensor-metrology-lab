# Project History

This file is the concise chronological engineering history of the **Virtual Sensor Metrology Lab** project.

Historical entries HO-001 through HO-005 were created before the repository scope was explicitly separated from the downstream DS 7140 course analysis. They are preserved as part of the laboratory's engineering history.

It complements, but does not replace, the detailed handoff documents in `docs/handoffs/`.

## History rule

For every completed task or milestone:

1. Work must begin on a new task-specific branch created from `main`.
2. Technical work and verification must be completed on that branch.
3. An English handoff must be created under `docs/handoffs/`.
4. The handoff must be registered in `docs/handoffs/HANDOFF_INDEX.md`.
5. This `PROJECT_HISTORY.md` file must be updated with a concise milestone entry.
6. A pull request may then be opened and merged back to `main` after verification.

The history entry should record the engineering outcome, verification/gate status, and the branch used. Detailed implementation notes belong in the corresponding handoff, not here.

---

## 2026-10-01 — HO-001 — Repository Bootstrap and SV-001

**Branch:** `chore/bootstrap-repository-structure`

Established the repository architecture, protected private-truth paths, added the initial static simulator verification fixture, and formalized the branch/handoff workflow.

**Verification:** `SV-001 = PASS (8/8)`

**Key outcome:** The static generator was verified for deterministic DUT/reference behavior, quantization, repeatability noise, chamber stability, day/run hierarchy, reproducibility, and analyst/private separation.

**Handoff:** `docs/handoffs/HO-001_REPOSITORY_BOOTSTRAP_AND_SV001.md`

---

## 2026-10-01 — HO-002 — SV-002 Dynamic Generator Verification

**Branch:** `feature/sv002-dynamic-verification`

Added analytical and numerical verification of the dynamic simulator, including first-order step response, dead time, t90, tau recovery, rise/fall asymmetry, cascaded chamber/reference/DUT response, reproducibility, private/public separation, and sampling-resolution effects.

**Verification:** `SV-002 = PASS (10/10)`

**Key outcome:** The dynamic generator was verified against known analytical first-order behavior before being used as reusable project infrastructure.

**Handoff:** `docs/handoffs/HO-002_SV002_DYNAMIC_VERIFICATION.md`

---

## 2026-10-01 — HO-003 — Core Simulator Refactor

**Branch:** `refactor/core-simulator-modules`

Refactored previously verified static and dynamic behavior into reusable `src/` modules for chamber, reference, DUT, DAQ, dynamics, simulation, and random-number utilities without changing verified behavior.

**Verification:** `SV-001 = PASS`, `SV-002 = PASS` after refactor.

**Key outcome:** The project gained a reusable simulator core while preserving the verified static and dynamic behavior and keeping final hidden DUT truth unfrozen.

**Handoff:** `docs/handoffs/HO-003_CORE_SIMULATOR_REFACTOR.md`

---

## 2026-10-01 — HO-004 — Experimental Design Matrix

**Branch:** `feature/experimental-design-matrix`

Implemented the programmatic experimental-design layer before freezing final hidden simulator truth.

**Verification:** `ED-001 = PASS (11/11)`

**Key outcome:** The project now has a reproducible test matrix covering the balanced 252-condition static DOE, calibration/validation roles, dynamic step/ramp/cyclic/sinusoidal tests, stability/drift checks, and uncertainty-evaluation points.

**Handoff:** `docs/handoffs/HO-004_EXPERIMENTAL_DESIGN_MATRIX.md`

---

## 2026-10-01 — HO-005 — Project History Ledger

**Branch:** `docs/project-history-ledger`

Introduced this independent project-history ledger and made history maintenance a permanent repository workflow requirement alongside task-specific branches, handoffs, and the handoff index.

**Verification:** Documentation consistency review.

**Key outcome:** Future project continuity is now represented at three levels: concise chronological history, authoritative handoff index, and detailed per-task handoffs.

**Handoff:** `docs/handoffs/HO-005_PROJECT_HISTORY_LEDGER.md`

---

## 2026-10-01 — HO-006 — Laboratory Scope Separation

**Branch:** `refactor/synthetic-metrology-lab-scope`

Separated the virtual laboratory and synthetic-data-generation work from the future DS 7140 analysis project before hidden truth or the final measurement dataset was frozen.

**Verification:** Repository architecture and information-boundary consistency review; existing `SV-001`, `SV-002`, and `ED-001` artifacts preserved unchanged.

**Key outcome:** This repository is now explicitly the **Virtual Sensor Metrology Lab**. It owns simulator physics, private truth, experiment design, measurement generation, and analyst-facing dataset release. Downstream EDA, ANOVA, calibration, blind validation, uncertainty analysis, Monte Carlo analysis, compliance decisions, notebooks, and course report will live in a separate DS 7140 repository created after the first frozen dataset release.

A formal interface contract was added at `docs/02_LAB_TO_DS7140_INTERFACE.md`, and `data/generated/` was established as the release boundary.

**Handoff:** `docs/handoffs/HO-006_LAB_SCOPE_SEPARATION.md`

---

## 2026-10-01 — HO-007 — Repository Front Page Refresh

**Branch:** `docs/refresh-repository-front-page`

Refreshed the repository landing page so the visible project identity, laboratory-only scope, public/private information boundary, frozen-dataset handoff contract, verified baseline, and current roadmap are immediately clear.

**Verification:** Documentation consistency review; simulator code and existing verification gates unchanged.

**Key outcome:** The README now matches the renamed `virtual-sensor-metrology-lab` repository and states explicitly that the project is still constructing the virtual laboratory; the final DS 7140 dataset has not yet been generated.

**Handoff:** `docs/handoffs/HO-007_REPOSITORY_FRONT_PAGE_REFRESH.md`

---

## 2026-10-03 — HO-008 — Public / Private Configuration Boundary

**Branch:** `feature/public-private-config-boundary`

Implemented the executable information boundary between analyst-visible laboratory specifications and simulator-only hidden truth.

Added the canonical tracked public specification at `config/public/lab_spec_v1.json`, a protected private loader and analyst-output leakage gate in `src/config_boundary.py`, and explicit policy documentation for `config/private/` and `data/private_truth/`.

**Verification:** `CB-001 = PASS (11/11)`

**Key outcome:** Public configuration can now be loaded and released independently of private simulator truth. Private truth loading is restricted to `config/private/`, private paths remain Git-protected, and analyst-facing serialization fails closed when simulator-only fields are detected. No final hidden DUT/reference/chamber values were frozen in this milestone.

**Handoff:** `docs/handoffs/HO-008_PUBLIC_PRIVATE_CONFIG_BOUNDARY.md`

---

## 2026-10-03 — HO-009 — Hidden Laboratory Personality Freeze

**Branch:** `feature/freeze-hidden-lab-personality`

Generated and sealed the final simulator-only DUT/reference/chamber personality outside Git, including static behavior, hierarchical random effects, drift, dynamics, chamber/reference behavior, and deterministic RNG policy.

**Verification:** `HP-001 = PASS (8/8)`

**Key outcome:** The laboratory now has one frozen private personality identified as `VSM-LAB-HP-v1`. Exact values remain local under `config/private/`; Git records only a SHA-256 commitment and a verification gate. The hidden design was accepted only after confirming a deliberate mixture of pass-like, borderline-like, and fail-like proxy behavior without disclosing which metrics belong to which category.

**Handoff:** `docs/handoffs/HO-009_HIDDEN_LAB_PERSONALITY_FREEZE.md`

---

## Current engineering state

The virtual laboratory has passed the static and dynamic simulator verification gates, the experimental design is verified, the public/private configuration boundary has passed CB-001, and the final hidden laboratory personality is now frozen and cryptographically committed.

The repository boundary remains explicit: this repository stops at the frozen analyst-facing dataset release. A separate DS 7140 repository will begin from that release.

The next technical milestone is to execute the full synthetic measurement campaign from the sealed private personality, generate analyst-facing static/dynamic/stability datasets plus protected private truth, verify campaign integrity, and freeze the first dataset release.
