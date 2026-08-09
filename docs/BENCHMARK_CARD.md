# PipelineProof benchmark card

## Overview

**PipelineProof** is an execution-based benchmark and RL environment for evaluating whether coding agents can repair **silent machine-learning pipeline integrity failures**. The benchmark is intentionally narrower than general software engineering or end-to-end AutoML benchmarks: it focuses on cases where a repository can execute, preserve an apparently reasonable interface, and pass visible tests while the resulting ML pipeline is still methodologically invalid.

The current public development release contains six defect families and a trusted verifier with family-specific held-back interventions.

## Research question

> Can an executable held-back verifier distinguish a genuinely repaired ML pipeline from a candidate that merely makes public tests pass or otherwise appears repaired?

The release separates that question from the later empirical question of how well any particular frontier model performs on the benchmark. The verifier, task generator, attack battery, valid controls, and reporting path can be audited without paid model calls.

## Intended use

PipelineProof is intended for:

- evaluating coding or ML-engineering agents on repository repair;
- RL or search environments requiring graded executable reward;
- studying public-test overfitting and verifier gaming;
- comparing pass@1 or best-of-N repair behaviour when external rollout traces are available;
- developing and auditing held-back behavioural verifiers for ML code.

## Non-intended use

The current release should not be used as evidence that:

- a model can autonomously conduct general ML research;
- the verifier is secure against arbitrary hostile code;
- the six tasks cover the distribution of production ML failures;
- public development-set scores are contamination resistant;
- zero false accepts on the released battery proves universal verifier soundness.

## Unit of evaluation

A task is a small repository with:

- `ISSUE.md` describing a behavioural symptom;
- `manifest.json` defining public task metadata;
- `run_pipeline.py` exposing the command interface;
- source code under `src/**`;
- public tests;
- example data.

The agent may modify source code but not protected evaluation surfaces.

## Defect families

| Family | Silent failure | Hidden integrity idea |
|---|---|---|
| Feature schema | prediction depends on accidental feature ordering | semantic invariance to feature-key presentation |
| Preprocessing/eval leakage | evaluation data influences fitted preprocessing | artifact invariance to evaluation-set substitution |
| Serialization | required preprocessing state is omitted | batch-composition invariance after round trip |
| Wrong evaluation split | metric is computed on training rows | agreement with trusted held-out metric |
| Group leakage | related records cross train/eval boundary | zero hidden group overlap |
| Target leakage | target-derived metadata enters features | prediction invariance to target-metadata perturbation |

See `TASK_TAXONOMY.md` for the complete behavioural specification.

## Verifier dimensions

Every candidate is checked for:

1. interface validity;
2. public-test success;
3. hidden functional correctness;
4. a family-specific causal/integrity contract;
5. persistence or deterministic repeatability;
6. protected-surface integrity.

Binary success requires every check to pass. The graded reward additionally exposes partial progress for RL/search use. See `VERIFIER_SPEC.md` and `REWARD_SPEC.md`.

## Public and held-back information

### Public

- issue description;
- public repository source;
- example data;
- public tests;
- command interface;
- public task metadata.

### Held back from the solving workspace

- private task specifications;
- private seeds;
- hidden generated probes;
- trusted expected values;
- gold/reference repairs used for evaluation development.

The public development tasks are not claimed to be contamination resistant. Consequential model comparisons should use separately distributed private evaluation material.

## Valid repair controls

Each of the six public development families has three legitimate repair styles:

- `canonical`
- `alternative`
- `refactor`

This produces **18 structural valid-repair cells**. Their purpose is to test that the verifier accepts multiple behaviourally correct implementations rather than encoding a single source-level patch.

The v0.4 evidence schema repeats these controls over seeds but reports structural cells separately from repetitions.

## Adversarial battery

The v0.4 battery contains **13 structural attack cells** before seed repetition:

- seven feature-schema attacks targeting public-test overfit, semantic gaming, output protocol, self-reported metrics, oracle access, and candidate-side evaluator manipulation;
- one otherwise-correct protected-surface tamper on each of the six defect families.

Each attack declares:

- an attack identifier;
- category;
- task;
- required preconditions;
- intended verifier detector;
- expected outcome.

Rejected malformed fixtures are not automatically counted as soundness evidence. Trials are classified as `INVALID_ATTACK`, `ACCEPTED_ATTACK`, `REJECTED_ATTACK`, or `REJECTED_OTHER_CHECK`.

See `THREAT_MODEL.md`, `VERIFIER_SPEC.md`, and generated `attack_matrix.csv`.

## Evidence protocol

The canonical evidence command is:

```bash
pipelineproof reproduce \
  --output results/reproduced \
  --seeds 4 \
  --mode docker
```

The reproduction bundle includes:

- task catalog;
- soundness receipt;
- attack matrix in JSON and CSV;
- valid-repair matrix in JSON and CSV;
- reward ladder in JSON and CSV;
- family controls;
- stability report;
- local/Docker parity report;
- sandbox manifest;
- environment metadata;
- source hashes;
- machine-readable summary;
- human-readable `summary.md`.

## Statistical reporting

False-accept and false-reject receipts include Wilson 95% confidence intervals.

Repeated seeds are **not** described as independent structural tasks. The release reports:

- number of distinct structural attack cells;
- number of repeated attack trials;
- number of valid attack trials entering the denominator;
- number of invalid attack fixtures excluded;
- number of distinct structural valid-repair cells;
- repeated valid-repair trials.

This prevents seed repetition from being presented as task diversity.

## Execution modes

### Docker

Docker is the canonical scored path. The container configuration uses restricted mounts and resources and disables network access under the scored policy.

### Local

Local mode is retained for rapid development and deterministic debugging. It is not treated as an equivalent security boundary.

The v0.4 evidence workflow runs the full structural battery through Docker and separately compares local and Docker outcomes.

## Model evaluation

PipelineProof does not call model providers directly. A harness may write one JSON object per rollout using the schema in `MODEL_EVALUATION.md`.

The reporting command:

```bash
pipelineproof model-report \
  --input results/model-rollouts.jsonl \
  --output results/model-report
```

produces:

- a task-clustered model panel;
- best-of-N curves;
- failure counts.

No frontier-model leaderboard is part of the zero-cost verifier evidence. Synthetic or fixture rollouts used to test reporting must be labelled as fixtures, never as empirical model results.

## Known limitations

- six compact deterministic public development tasks;
- linear/small-model task construction rather than large production training stacks;
- finite adversarial battery;
- public tasks may eventually become training data;
- private evaluation coverage is not publicly auditable without revealing it;
- Docker reduces but does not eliminate hostile-code risk;
- no empirical frontier-model trajectories in the current zero-cost release;
- verifier thresholds and reward weights are benchmark design choices rather than production utility calibration.

## Reproducibility

The package is installable and tested through CI. Release CI validates source installation, wheel installation, Docker execution, full evidence generation, evidence invariants, and model-report generation.

The generated environment record includes Python/platform information, seed count, execution mode, attack-battery version, and sandbox metadata. Source hashes exclude transient version-control, build, cache, and evidence-output state.

## Versioning

The v0.3 baseline evidence is frozen under `results/archive/v0.3.0/BASELINE.md` by immutable Git commit and blob hashes.

The v0.4 hardening pass changes the **evidence schema and attack validation**, not the conceptual six-family benchmark scope. In particular, v0.4 separates structural coverage from seed repetitions and excludes invalid attack fixtures from the soundness denominator.

## Citation

Until a formal paper or archival software release is supplied, cite the repository and exact version/commit used for evaluation. A future `CITATION.cff` release artifact can provide a preferred citation without changing benchmark semantics.
