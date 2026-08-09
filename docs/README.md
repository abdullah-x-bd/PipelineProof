# PipelineProof research documentation

Use this directory as the research-facing specification for the benchmark.

## Start here

- `BENCHMARK_CARD.md` defines the intended and non-intended uses, benchmark unit, evidence protocol, limitations, and reproducibility contract.
- `TASK_TAXONOMY.md` defines the six silent ML-integrity failure families.
- `VERIFIER_SPEC.md` defines the hidden interventions, checks, and thresholds.
- `REWARD_SPEC.md` defines the graded reward and functional gating.

## Validity and security

- `THREAT_MODEL.md` defines trusted and untrusted components, covered attacks, sandbox assumptions, and residual risks.
- `RELATED_WORK.md` positions PipelineProof relative to repository repair, ML engineering, silent-error detection, and leakage research.

## Evaluation and release

- `MODEL_EVALUATION.md` defines the provider-neutral model-rollout record and aggregation protocol.
- `RELEASE_PROCESS.md` defines the canonical Docker evidence procedure and non-self-referential provenance rule.

## Machine-readable contracts

The corresponding machine-readable schemas are in the repository-level `schemas/` directory:

- `schemas/evidence-summary.schema.json`
- `schemas/model-rollout.schema.json`

The canonical evidence is stored under `results/public/v0.4.0/` and can be checked with:

```bash
pipelineproof validate-evidence --input results/public/v0.4.0
```

The release-level checklist is `RELEASE_CHECKLIST.md` at the repository root.
