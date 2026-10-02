# HO-007 — Repository Front Page Refresh

## Milestone identity

- Project: Virtual Sensor Metrology Lab
- Branch: `docs/refresh-repository-front-page`
- Date: 2026-10-01
- Scope: Refresh the repository front page so the README matches the renamed repository and the clarified laboratory-only scope

## Objective

Update the repository landing page so a reader can immediately understand that this repository is a **virtual metrology laboratory and synthetic measurement dataset generator**, not the downstream DS 7140 analysis project.

## Changes

1. Renamed the README title to **Virtual Sensor Metrology Lab** to match the GitHub repository name.
2. Reframed the opening description around a reproducible virtual metrology laboratory.
3. Clarified the laboratory measurement chain and the separate hidden-truth path.
4. Made repository ownership explicit: chamber, reference, DUT, DAQ, experiment design, verification, hidden truth, measurement campaign, and dataset release.
5. Made downstream DS 7140 analysis explicitly out of scope for this repository.
6. Clarified the public/analyst-visible versus private/simulator-only information boundary.
7. Defined `data/generated/` as the formal frozen dataset release boundary.
8. Added a concise current-stage roadmap showing that the project is still constructing the laboratory and has not yet generated the final course dataset.
9. Preserved the permanent branch → verification → handoff/index/history → PR → merge workflow.

## Verification

Documentation consistency review performed against the current repository architecture and HO-006 scope separation.

Checks:

- README title matches repository identity: **PASS**
- Laboratory-only scope is explicit: **PASS**
- DS 7140 downstream analysis is clearly separated: **PASS**
- Public/private truth boundary is explicit: **PASS**
- Dataset release boundary is explicit: **PASS**
- Current project stage is explicit: **PASS**
- Existing simulator verification status remains unchanged: **PASS**

No simulator code, hidden parameters, experimental-design logic, or generated datasets were changed by this documentation task.

## Engineering outcome

The repository landing page now reflects the intended project architecture:

```text
Virtual Sensor Metrology Lab
    -> verified simulator
    -> hidden truth
    -> synthetic measurement campaign
    -> frozen dataset release
    -> separate DS 7140 analysis repository
```

## Next technical milestone

Define and verify the public/private configuration boundary before freezing final DUT/reference/chamber truth.
