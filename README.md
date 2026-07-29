# PipelineProof

PipelineProof is an RL environment for repairing non-crashing machine-learning pipeline integrity failures. It evaluates whether a coding agent preserves legitimate boundaries between training, evaluation, and deployment by using hidden interventions and metamorphic tests rather than patch matching or self-reported metrics.

## Status

Early research and engineering build for the Tensium RL Environment Trial.

The initial scope covers three integrity contracts:

1. Training-data provenance
2. Evaluation validity
3. Train-serving equivalence

The first milestone is a complete vertical slice for one defect family, including an original task repository, a gold repair, alternative correct repairs, a trusted verifier, adversarial cheats, sandbox execution, and a reproducible soundness report.

## Public and private boundaries

This repository contains the environment package, public task material, public tests, documentation, and reproducibility code. Hidden evaluation assets, oracle material, private seeds, raw model credentials, and unreleased result bundles must not be committed.

## Development setup

Requirements:

- Python 3.11 or newer
- `uv`, recommended, or `pip`

Using `uv`:

```bash
uv sync --all-extras --dev
uv run pytest
uv run pipelineproof doctor
```

Using `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest
pipelineproof doctor
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Current commands

```bash
pipelineproof doctor
pipelineproof show-plan
pytest
```

## Project layout

```text
src/pipelineproof/        Environment package
tasks/public/             Public task instances and fixtures
tests/                    Package and contract tests
attacks/                  Versioned adversarial cheat implementations
docs/                     Design, measurement, and planning documents
scripts/                  Reproducibility and analysis entry points
results/public/           Public aggregate results only
```

## Design principles

- Score repository behaviour, not the agent's claim of success.
- Accept multiple correct implementations.
- Keep reference assets outside the solving agent's filesystem.
- Treat false-accept and false-reject rates as measured properties of a versioned test battery.
- Report uncertainty at the defect-family level when generated instances are correlated.
- Preserve raw evidence for every headline result.

## Roadmap

The detailed implementation plan is in [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md).

## License

No licence has been selected yet. All rights are reserved until a licence is added explicitly.
