# PipelineProof

PipelineProof is an execution-based RL environment for repairing non-crashing machine-learning pipeline failures.

It tests six integrity failures:

1. Feature-schema mismatch
2. Evaluation data used during preprocessing
3. Missing preprocessing state after serialization
4. Evaluation on the wrong split
5. Group leakage across splits
6. Target-derived feature leakage

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pipelineproof doctor
pytest
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

## Generate development tasks

```bash
pipelineproof generate --output tasks/public
```

## Verify a candidate

```bash
pipelineproof verify \
  --task feature-schema-a \
  --candidate controls/feature-schema-a/canonical \
  --mode local
```

`local` mode applies time and resource limits but does not provide network or filesystem isolation.

For scored runs:

```bash
docker build -f docker/task.Dockerfile -t pipelineproof-task:0.3.0 .

pipelineproof verify \
  --task feature-schema-a \
  --candidate controls/feature-schema-a/canonical \
  --mode docker
```

## Reproduce evidence

```bash
pipelineproof reproduce --output results/reproduced --seeds 4 --mode local
```

The generated release manifest excludes Git metadata, virtual environments, build outputs, package metadata, and the evidence output directory itself.

The committed evidence includes:

- Six development tasks
- Eighteen valid repair controls
- Eight attack classes
- Thirty-two attack trials
- Twelve valid-solution trials
- A graded reward ladder
- An independent quality suite
- Four-seed stability checks

The observed local-mode soundness results are zero false accepts in 32 trials and zero false rejects in 12 valid-solution trials. Confidence intervals are reported in `results/public/soundness_receipt.json`.

## Analyze model rollouts

Store one rollout per line using the schema in `docs/MODEL_EVALUATION.md`, then run:

```bash
pipelineproof model-report \
  --input results/model-rollouts.jsonl \
  --output results/model-report
```

The command produces a lower-bound-ranked model panel, best-of-N curves, and failure counts.

## Private evaluation bundle

Evaluation specifications, held-back tasks, gold repairs, and private seeds are not committed. The trusted verifier receives them separately. The solving agent receives only one task repository.

## Current limit

No frontier-model leaderboard or model-generated best-of-N experiment has been run. The execution and reporting path is implemented, but real model trajectories still require model access.
