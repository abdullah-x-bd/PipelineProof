# Reproducibility

## Package

```bash
python -m pip install -e ".[dev]"
pytest
pipelineproof doctor
```

## Full integration tests

```bash
pytest -o addopts="-ra --strict-markers" -m slow
```

## Development tasks

```bash
pipelineproof generate --output tasks/public
```

## Evidence

```bash
pipelineproof reproduce --output results/reproduced --seeds 4 --mode local
```

The command writes the soundness receipt, family controls, reward ladder, stability report, sandbox manifest, candidate-search sanity check, summary, and a source manifest. The source manifest excludes Git metadata, virtual environments, package metadata, build outputs, and the evidence directory.

## Wheel

```bash
python -m build
python -m venv /tmp/pipelineproof-clean
/tmp/pipelineproof-clean/bin/python -m pip install dist/pipelineproof-0.3.0-py3-none-any.whl
/tmp/pipelineproof-clean/bin/pipelineproof doctor
```

## Model results

```bash
pipelineproof model-report \
  --input results/model-rollouts.jsonl \
  --output results/model-report
```

## Private evaluation

Keep the private bundle outside the agent workspace. Pass one private specification to the trusted verifier with `--spec`.
