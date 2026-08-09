# PipelineProof

**PipelineProof is an execution-based benchmark and RL environment for repairing silent machine-learning pipeline integrity failures.**

A PipelineProof task can execute, preserve the expected command interface, and pass visible tests while still being methodologically invalid. The benchmark therefore scores candidate repairs with a trusted held-back verifier rather than treating public-test success as sufficient evidence of correctness.

<p align="center">
  <img src="figures/architecture.svg" alt="PipelineProof benchmark architecture" width="900" />
</p>

## What PipelineProof evaluates

The public development suite contains six defect families:

| Family | Silent failure | Held-back contract |
|---|---|---|
| Feature schema | predictions depend on accidental feature ordering | semantic invariance to key-order presentation |
| Preprocessing leakage | evaluation rows influence fitted preprocessing | artifact invariance to evaluation-set substitution |
| Serialization | required preprocessing state is not persisted | batch-composition invariance after round trip |
| Wrong evaluation split | reported metric uses training rather than evaluation rows | agreement with independently computed held-out RMSE |
| Group leakage | related records cross the train/evaluation boundary | zero group overlap with exact row coverage |
| Target leakage | target-derived metadata enters the feature set | invariance to target-metadata perturbation |

The exact interventions and thresholds are documented in [`docs/TASK_TAXONOMY.md`](docs/TASK_TAXONOMY.md) and [`docs/VERIFIER_SPEC.md`](docs/VERIFIER_SPEC.md).

## Research-artifact design

PipelineProof treats verifier validity as part of the benchmark rather than an implementation detail.

The v0.4 research-artifact evidence schema audits:

- **13 structural adversarial cells** before seed repetition;
- **18 structural legitimate repair cells**, comprising three repair implementations for each of six families;
- malformed or otherwise invalid attack fixtures separately from genuine verifier rejections;
- the intended detector for each attack rather than merely checking that a candidate failed somewhere;
- a strictly ordered graded reward ladder;
- deterministic stability over repeated seeds;
- full Docker execution of the attack and valid-control batteries;
- local-versus-Docker outcome parity;
- source and environment provenance.

Repeated seeds are reported separately from structural task or attack diversity.

<p align="center">
  <img src="figures/attack_matrix.svg" alt="PipelineProof adversarial verifier coverage" width="900" />
</p>

## Verifier contract

Every candidate is checked along six dimensions:

1. command interface;
2. public tests;
3. hidden functional correctness;
4. family-specific causal or integrity contract;
5. persistence or deterministic repeatability;
6. protected evaluation surface.

A candidate passes only when **all six checks pass** and the total reward is `1.0`.

The graded reward is:

```text
R = 0.10 interface
  + 0.10 public_tests
  + 0.25 functional
  + 0.35 (causal AND functional)
  + 0.10 (persistence AND functional)
  + 0.10 protected
```

Causal and persistence credit are gated on hidden functional correctness so a constant but invariant predictor is not rewarded as if it had solved the task. See [`docs/REWARD_SPEC.md`](docs/REWARD_SPEC.md).

<p align="center">
  <img src="figures/reward_ladder.svg" alt="PipelineProof graded reward ladder" width="900" />
</p>

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pipelineproof doctor
pytest
```

Windows PowerShell activation:

```powershell
.venv\Scripts\Activate.ps1
```

## Generate the development tasks

```bash
pipelineproof generate --output tasks/public
```

## Verify a candidate

For fast local development:

```bash
pipelineproof verify \
  --task feature-schema-a \
  --candidate controls/feature-schema-a/canonical \
  --mode local
```

Local mode applies process and resource limits but is **not** the canonical scored security boundary.

For scored execution, build the benchmark container and use Docker mode:

```bash
docker build -f docker/task.Dockerfile -t pipelineproof-task:0.3.0 .

pipelineproof verify \
  --task feature-schema-a \
  --candidate controls/feature-schema-a/canonical \
  --mode docker
```

**Docker is the canonical scored mode.** The threat model and residual security assumptions are documented in [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md).

## Reproduce the research evidence

Canonical reproduction:

```bash
pipelineproof reproduce \
  --output results/reproduced \
  --seeds 4 \
  --mode docker
```

The evidence bundle contains:

```text
task_catalog.json
soundness_receipt.json
attack_matrix.json
attack_matrix.csv
valid_repair_matrix.json
valid_repair_matrix.csv
reward_ladder.json
reward_ladder.csv
family_controls.json
stability.json
stability.csv
candidate_search.json
sandbox_manifest.json
local_docker_parity.json
environment.json
summary.json
summary.md
release_hashes.json
```

`summary.md` is generated for human inspection. The JSON/CSV artifacts preserve the trial-level and structural evidence needed for audit or downstream analysis.

The release gate requires:

- no invalid attack fixtures entering the soundness denominator;
- no accepted attacks in the released battery;
- no rejected legitimate repairs;
- no unintended-detector-only rejections in the structural attack battery;
- a strictly monotonic reward ladder;
- zero local/Docker outcome disagreements across the structural attack and legitimate repair cells.

The canonical GitHub Actions job runs the full evidence path in Docker and uploads the complete bundle.

## Evidence provenance

The previous v0.3.0 public evidence is preserved rather than overwritten. Its immutable source commit and artifact blob hashes are recorded in [`results/archive/v0.3.0/BASELINE.md`](results/archive/v0.3.0/BASELINE.md).

The v0.4 evidence schema deliberately changes how robustness is reported. In particular, it separates structural coverage from repeated seeds and excludes malformed attack fixtures from the false-accept denominator.

## Model evaluation

PipelineProof is provider-neutral. It does not call model APIs directly.

An external harness writes one JSON object per rollout using the schema in [`docs/MODEL_EVALUATION.md`](docs/MODEL_EVALUATION.md), then runs:

```bash
pipelineproof model-report \
  --input results/model-rollouts.jsonl \
  --output results/model-report
```

The report contains:

- a task-clustered model panel;
- best-of-N curves;
- failure counts.

No frontier-model leaderboard is claimed by the zero-cost verifier artifact. Synthetic reporting fixtures are not empirical model results.

## Private evaluation

The solving agent receives one task repository. Private evaluation specifications, held-back tasks, gold/reference repairs, and private seeds remain outside the agent workspace and are supplied to the trusted verifier separately.

Public development tasks are inspectable and may eventually become training data. Public scores should therefore not be presented as contamination-resistant evidence.

## Documentation

- [`docs/BENCHMARK_CARD.md`](docs/BENCHMARK_CARD.md) — complete benchmark card
- [`docs/TASK_TAXONOMY.md`](docs/TASK_TAXONOMY.md) — six failure families
- [`docs/VERIFIER_SPEC.md`](docs/VERIFIER_SPEC.md) — exact hidden interventions and thresholds
- [`docs/REWARD_SPEC.md`](docs/REWARD_SPEC.md) — reward construction and gating
- [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) — trust boundary, attacks, and residual risks
- [`docs/MODEL_EVALUATION.md`](docs/MODEL_EVALUATION.md) — provider-neutral rollout schema and aggregation
- [`docs/RELATED_WORK.md`](docs/RELATED_WORK.md) — positioning relative to repository-agent, ML-engineering, silent-error, and leakage research

<p align="center">
  <img src="figures/task_taxonomy.svg" alt="PipelineProof task taxonomy" width="900" />
</p>

## Scope and limitations

PipelineProof currently uses six compact deterministic public development tasks and small controlled models. The released adversarial battery is finite. Docker reduces the candidate execution surface but is not claimed to be an absolute hostile-code security boundary. The benchmark does not yet establish frontier-model performance or cover the full distribution of production ML failures.

The precise supported claim is narrower:

> Under the released task set, attack constructions, seeds, and execution configuration, the verifier can be audited for whether it accepts the released legitimate repairs and rejects the released adversarial battery through the reported checks.

See the benchmark card and threat model before using PipelineProof for consequential model comparisons.
