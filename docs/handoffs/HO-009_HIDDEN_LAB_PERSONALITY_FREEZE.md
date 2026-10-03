# HO-009 — Hidden Laboratory Personality Freeze

## Milestone identity

- **Project:** Virtual Sensor Metrology Lab
- **Handoff:** HO-009
- **Branch:** `feature/freeze-hidden-lab-personality`
- **Gate:** `HP-001 — Hidden Personality Verification`
- **Date:** 2026-10-03

## Objective

Freeze the final simulator-only DUT/reference/chamber laboratory personality before the full synthetic measurement campaign, while keeping every exact hidden parameter outside Git history and outside the future analyst-facing data path.

## Engineering decision

The final laboratory personality is represented by one local JSON file:

```text
config/private/final_lab_personality_v1.json
```

That file is protected by the repository's existing `config/private/*` ignore rule and must never be committed.

The repository records only a cryptographic commitment to the frozen private file:

```text
config/public/private_personality_commitment_v1.json
```

The commitment contains the personality identifier, canonicalization rule, and SHA-256 digest. It proves later that the simulator used the same frozen hidden personality without revealing the values themselves.

## Hidden domains frozen

The sealed private personality contains final simulator-only values for:

- DUT static behavior: offset, gain, nonlinearity, temperature effect, RH-temperature interaction, hysteresis, repeatability, resolution
- DUT hierarchical effects: day and run variation
- DUT drift law
- DUT dynamics: rise/fall time constants, dead time, temperature dependence
- reference-instrument static error, repeatability, resolution, drift, and dynamics
- chamber setpoint bias, spatial offsets, stability, temperature behavior, rise/fall dynamics, delay, overshoot, and cycling
- random-effect distribution policy
- deterministic campaign RNG master seed and stream policy

No exact values are recorded in this handoff, report, README, repository history, or Git-tracked source.

## Commitment

- **Personality ID:** `VSM-LAB-HP-v1`
- **Algorithm:** SHA-256
- **Digest:** `e534c04fb3718b4ae1dfe911c369bde3e1c37d922aaffeaa66bf400ebdbc1998`
- **Canonicalization:** JSON object serialized with sorted keys and compact separators before hashing

## Verification — HP-001

`verification/HP-001_Hidden_Personality/hp001_hidden_personality_verification.py` verifies the private file locally without printing exact hidden values.

Checks:

1. commitment identity
2. protected private-path loading
3. private schema version
4. SHA-256 commitment equality
5. presence of required hidden domains
6. basic physical/range sanity
7. deterministic campaign seed presence
8. deliberate mixture of pass / borderline / fail proxy behavior

**Result:** `HP-001 = PASS (8/8)`

The curated tracked report records only gate status and the public digest; metric-level hidden classifications remain private.

## Behavioral-design policy

The hidden personality was deliberately accepted only when its proxy behavior included at least one pass-like, one borderline-like, and one fail-like condition among selected public acceptance dimensions. This prevents the eventual DS 7140 dataset from degenerating into an unrealistically all-pass or all-fail validation exercise.

The downstream analyst is not told which metrics fall into which category. Those outcomes must be inferred from the released measurements.

## Reproducibility policy

The private personality includes a deterministic RNG master seed. Future campaign generation must load this same sealed private file and use the declared stream policy. The public SHA-256 commitment provides an immutable audit reference.

Any change to a hidden parameter, including the seed, creates a different digest and therefore constitutes a new personality version rather than a silent edit.

## Local installation requirement

Before campaign generation, the sealed file supplied outside Git must be copied to:

```text
config/private/final_lab_personality_v1.json
```

Then run:

```powershell
conda activate DS
python verification\HP-001_Hidden_Personality\hp001_hidden_personality_verification.py
```

Expected result:

```text
HP-001: 8/8 checks PASS
Commitment verified. Exact hidden values remain undisclosed.
```

## Repository impact

Tracked additions for this milestone:

- public SHA-256 commitment
- HP-001 verification script
- curated HP-001 result report
- documentation of the freeze and local verification process

Tracked content does **not** include the private personality itself.

## Next milestone

The laboratory is now allowed to proceed to the **full synthetic measurement campaign**. The next task should load the sealed private personality, execute the verified experimental design, generate all static/dynamic/stability analyst-facing datasets, produce private truth only in protected paths, run campaign-level verification, and prepare the first frozen dataset release.
