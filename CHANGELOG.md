# Changelog

All notable benchmark and release-artifact changes are recorded here.

## 0.4.0 — 2026-08-09

### Research artifact

- Separated structural adversarial coverage from repeated seed trials.
- Added explicit attack validity and intended-detector classification.
- Repaired the historical hard-coded public-fixture attack so it executes as intended.
- Expanded the released battery to 13 structural attack cells.
- Audited all 18 structural legitimate-repair controls across the six task families.
- Added local/Docker structural parity reporting.
- Made Docker the canonical scored execution path.
- Added task taxonomy, verifier specification, reward specification, benchmark card, expanded threat model, and related-work positioning.
- Added architecture, taxonomy, attack-coverage, and reward-ladder figures.
- Added machine-readable and human-readable canonical evidence under `results/public/v0.4.0/`.
- Added source/environment provenance and Docker image identity.

### Release engineering

- Centralized the package version at `0.4.0`.
- Added evidence-bundle validation and SHA-256 evidence manifests.
- Added canonical reproduction and release-audit scripts.
- Added evidence and model-rollout JSON schemas.
- Added citation, contribution, security, and release-process metadata.
- Hardened CI to prevent recursive evidence-persistence runs.

### Claim boundary

- No frontier-model leaderboard is included in this release.
- No model-generated best-of-N result is claimed.
- Public development tasks are not claimed to be contamination resistant.
- Zero false accepts on the released battery is not presented as universal verifier soundness.

## 0.3.0 — 2026-07-29

- Established the six-family deterministic PipelineProof environment.
- Added trusted hidden verification, local and Docker execution modes, protected-file checks, graded reward, public controls, and the initial adversarial battery.
- Added four-seed stability evidence and provider-neutral model-reporting infrastructure.
- Preserved the original public evidence provenance under `results/archive/v0.3.0/BASELINE.md` during the v0.4 hardening pass.
