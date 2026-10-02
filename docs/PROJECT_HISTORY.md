# Project History

This file is the concise chronological engineering history of the **Full Sensor Validation & Metrology** project.

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

## Current engineering state

The simulator physics has passed the static and dynamic verification gates, the verified behavior has been refactored into reusable core modules, and the project-level experimental design has been defined and verified.

The next technical milestone is to define the final public/private configuration boundary and then freeze the hidden DUT/reference/chamber parameter set before generating the full synthetic validation dataset.
