# Release process

PipelineProof releases separate the source revision that is evaluated from the later commit that stores the resulting evidence. This avoids self-referential provenance.

## Release source

The canonical evidence must record the exact source revision supplied through `PIPELINEPROOF_SOURCE_COMMIT`. That revision is the code/configuration commit that was executed in CI. The subsequent evidence-only commit is not retroactively substituted as the source revision.

For v0.4.0 the release sequence is:

1. Finish code, tests, documentation, schemas, and version metadata on the release branch.
2. Run the full pull-request CI workflow.
3. Build `pipelineproof-task:0.4.0` in the canonical Docker evidence job.
4. Run the full Docker reproduction over four seeds.
5. Record the Docker image ID in `environment.json`.
6. Generate `MANIFEST.sha256` over the evidence bundle.
7. Run `pipelineproof validate-evidence` against the generated bundle.
8. Upload the exact validated bundle as a GitHub Actions artifact.
9. Persist that artifact under `results/public/v0.4.0/` with an evidence-only commit carrying `[skip ci]`.
10. Verify that the persisted bundle still passes `pipelineproof validate-evidence`.
11. Run `python scripts/release_audit.py`.
12. Merge only after the code revision that generated the evidence has passed all CI gates and the evidence-only diff contains no source changes.

The `[skip ci]` marker on the evidence-only commit is intentional. Without it, a newly committed evidence bundle would trigger another canonical evidence run whose `source_commit` would be the evidence commit, producing another changed bundle and creating a provenance feedback loop.

## Canonical reproduction

From a clean checkout with Docker available:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python scripts/reproduce_release.py --output results/reproduced/v0.4.0 --seeds 4
```

On Windows PowerShell, activate with:

```powershell
.venv\Scripts\Activate.ps1
```

The script builds the versioned Docker image, reproduces the evidence, records the image identity, writes the SHA-256 manifest, validates the bundle, and exits non-zero if a release invariant fails.

## Independent validation

Validate an existing canonical bundle without rerunning the benchmark:

```bash
pipelineproof validate-evidence --input results/public/v0.4.0
```

Regenerate its digest manifest after an intentional change:

```bash
pipelineproof evidence-manifest --input results/public/v0.4.0
```

A manifest should never be regenerated merely to hide an unexplained difference. Evidence changes must be traced to a deliberate source, configuration, seed, or environment change.

## Release audit

Run:

```bash
python scripts/release_audit.py
```

The audit checks the centralized version, required research/release files, citation metadata, and the committed canonical evidence.

## Versioning

The package version has one source of truth in `src/pipelineproof/_version.py`. Setuptools reads it dynamically from that module. The Docker sandbox image tag is derived from the same runtime version.

Changes to the attack battery or evidence schema are versioned separately inside the evidence metadata. The package release version therefore does not imply that every internal evidence sub-schema uses the same numbering scheme.

## Model results

Model-generated rollout results are not part of the verifier release unless they were actually run. Synthetic fixtures must use an unmistakable fixture route/model name and must never be copied into a leaderboard or empirical results table.

## Archival release

After merge, create the repository release/tag from the exact merged v0.4.0 revision and archive that revision with the preferred research-software archive used by the project. If an archival DOI is later assigned, add it to `CITATION.cff` in a metadata-only follow-up release rather than inventing a placeholder DOI.
