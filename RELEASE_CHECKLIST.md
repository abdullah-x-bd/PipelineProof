# PipelineProof v0.4.0 release checklist

## Source and package

- [x] Package version centralized in `src/pipelineproof/_version.py`.
- [x] Setuptools reads the version dynamically.
- [x] Docker sandbox image tag derives from the package version.
- [x] Python 3.11, 3.12, and 3.13 remain in the tested matrix.
- [x] Source and wheel installations are exercised in CI.
- [x] MIT license included and recorded in package/citation metadata.

## Benchmark validity

- [x] Six task families documented.
- [x] Hidden verifier interventions and thresholds documented.
- [x] Reward semantics documented and tested.
- [x] Thirteen structural adversarial cells defined separately from seed repetitions.
- [x] Invalid attack attempts excluded from soundness evidence.
- [x] Intended detector recorded for each released attack.
- [x] Eighteen structural legitimate repair cells audited.
- [x] Broken controls remain rejected.
- [x] Local/Docker structural parity is measured.

## Evidence

- [x] Canonical scored mode is Docker.
- [x] Evidence records exact source commit.
- [x] Evidence records Docker image identity.
- [x] Evidence includes machine-readable JSON and CSV outputs.
- [x] Evidence includes a human-readable summary.
- [x] Evidence bundle has SHA-256 manifest support.
- [x] `pipelineproof validate-evidence` enforces the release invariants.
- [x] Release hashes exclude transient Git, build, cache, and evidence-output paths.
- [x] v0.3 baseline remains frozen rather than overwritten.
- [x] Evidence persistence cannot recursively trigger new evidence commits.

## Research communication

- [x] README states the research question and claim boundary.
- [x] Benchmark card included.
- [x] Threat model included.
- [x] Task taxonomy included.
- [x] Verifier specification included.
- [x] Reward specification included.
- [x] Model-evaluation protocol included.
- [x] Related-work positioning included.
- [x] Four research figures included.
- [x] Changelog included.
- [x] `CITATION.cff` included.
- [x] Contribution and security policies included.
- [x] Structured issue and pull-request templates included.

## Model evaluation claim boundary

- [x] No frontier-model leaderboard is claimed without actual model trajectories.
- [x] No model-generated best-of-N experiment is claimed without actual model trajectories.
- [x] Synthetic rollout fixtures are unmistakably labelled as fixtures.
- [x] Public tasks are not described as contamination resistant.

## Final release gate

Before merging the release branch:

```bash
ruff check .
pytest
python scripts/release_audit.py
```

Canonical Docker CI must additionally pass the slow research-evidence suite, full Docker reproduction, evidence manifest generation, evidence validation, local/Docker parity audit, and artifact persistence.

After the canonical evidence-only commit, review its diff and confirm it changes only `results/public/v0.4.0/`. Merge only after that check.
