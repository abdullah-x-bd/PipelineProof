.PHONY: install test lint doctor check build

install:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check .

doctor:
	pipelineproof doctor

check: lint test doctor

build:
	python -m build
