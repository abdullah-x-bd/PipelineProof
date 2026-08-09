# PipelineProof v0.3.0 evidence baseline

This directory freezes the provenance of the public evidence that existed immediately before the v0.4 research-artifact hardening pass.

## Immutable source

- Baseline commit: `a34ed4066c14bbd65c89bf63fda0446079f422a3`
- Commit message: `Complete release audit and model reporting`
- Baseline evidence path: `results/public/`

The Git commit above is the canonical immutable copy. This archive records the artifact blob hashes and headline metrics so later releases do not silently reinterpret the July evidence.

## Artifact blob hashes

| Artifact | Git blob SHA |
|---|---|
| `task_catalog.json` | `fe4eb0c7f519c07c9415e405ce022d2cebd50b46` |
| `soundness_receipt.json` | `7e23a13ccd52c0cb787194b4330b6252b19a5f98` |
| `reward_ladder.json` | `52787c3a5f3cd3c44c5ac09bbcdd8c47f29f71ed` |
| `family_controls.json` | `306368148bab8f4573043f8224ac80c8537510d8` |
| `stability.json` | `8a31858f8f6d0d4e790f5f559377e4b6b9c56947` |
| `candidate_search.json` | `dec0e4617132a91670205a51e832ceb699f64b4b` |
| `sandbox_manifest.json` | `42bcfd95cf8adf9643f0a627eabd303ce5b4d9f4` |
| `summary.json` | `50f1976929c837ec46dabd3f6a8b7f5030f31f79` |

## Headline v0.3.0 evidence

The baseline summary reported:

- 6 development tasks across 6 failure families
- 18 accepted valid controls
- 6 rejected broken controls
- 0 false accepts in 32 repeated attack trials
- 0 false rejects in 12 repeated valid-solution trials on the feature-schema task
- a strictly monotonic five-level reward ladder
- 0 high-variance deterministic control cells
- Docker configured and separately exercised in CI, while the committed statistical receipt was local-mode evidence
- no frontier-model leaderboard and no model-generated best-of-N experiment

## Why v0.4 changes the evidence schema

The v0.3 receipt mixed structural coverage with repeated seeds and did not distinguish an accidentally malformed adversarial fixture from a clean verifier rejection. The v0.4 evidence schema therefore reports structural attack cells separately from repeated trials, excludes invalid attack fixtures from the soundness denominator, audits all 18 valid repair cells, and adds local/Docker parity evidence.
