# HO-005 — Project History Ledger

## Milestone identity

- Project: Full Sensor Validation & Metrology
- Branch: `docs/project-history-ledger`
- Date: 2026-10-01
- Scope: Introduce an independent chronological project-history ledger and make it a permanent workflow requirement

## Objective

Add a concise, repository-level history record that is separate from detailed handoffs and the handoff index.

The goal is to preserve project continuity at three complementary levels:

1. `docs/PROJECT_HISTORY.md` — concise chronological engineering history
2. `docs/handoffs/HANDOFF_INDEX.md` — authoritative registry of handoffs
3. `docs/handoffs/HO-xxx_*.md` — detailed task-level engineering continuity

## Previous verified milestones recorded

The new history ledger backfills the completed project milestones:

- `HO-001` — Repository Bootstrap and `SV-001`; `SV-001 = PASS (8/8)`
- `HO-002` — Dynamic Generator Verification; `SV-002 = PASS (10/10)`
- `HO-003` — Core Simulator Refactor; `SV-001 = PASS`, `SV-002 = PASS` after refactor
- `HO-004` — Experimental Design Matrix; `ED-001 = PASS (11/11)`

## Technical/documentation work completed

- Added `docs/PROJECT_HISTORY.md` as the chronological project ledger.
- Backfilled HO-001 through HO-004 with their branch, engineering outcome, verification state, and handoff reference.
- Added the HO-005 history entry for this workflow change.
- Updated the root `README.md` so project history is a mandatory continuity record for every completed task.
- Updated the README current milestone so it reflects the verified simulator core and experimental-design baseline rather than the earlier bootstrap state.
- Updated `docs/handoffs/HANDOFF_INDEX.md` to register this handoff.

## Permanent workflow decision

For every future completed task, the required sequence is now:

```text
new task-specific branch
-> technical work
-> verification
-> English handoff
-> HANDOFF_INDEX update
-> PROJECT_HISTORY update
-> pull request
-> merge to main
```

`PROJECT_HISTORY.md` is intentionally concise and append-oriented. Detailed implementation notes remain in the corresponding handoff document.

## Verification

Documentation consistency review confirms that:

- the history contains HO-001 through HO-005 in chronological order;
- the handoff index registers HO-001 through HO-005;
- the README defines all three continuity records;
- the next technical milestone remains the public/private configuration boundary and hidden simulator-truth freeze.

## Next technical milestone

Define the final public/private configuration boundary and freeze the hidden DUT/reference/chamber parameter set without exposing final private truth to analyst-facing notebooks or tracked repository data.
