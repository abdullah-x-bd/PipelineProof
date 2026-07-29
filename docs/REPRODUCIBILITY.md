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
pipelineproof reproduce --output results/public --seeds 4 --mode local
```

## Wheel

```bash
python -m build
python -m venv /tmp/pipelineproof-clean
/tmp/pipelineproof-clean/bin/python -m pip install dist/pipelineproof-0.3.0-py3-none-any.whl
/tmp/pipelineproof-clean/bin/pipelineproof doctor
```

## Private evaluation

Keep the private bundle outside the agent workspace. Pass one private specification to the trusted verifier with `--spec`.
