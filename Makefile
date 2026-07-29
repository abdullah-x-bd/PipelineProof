.PHONY: install test reproduce tasks task-image build check

install:
	python -m pip install -e ".[dev]"

test:
	pytest

tasks:
	pipelineproof generate --output tasks/public

reproduce:
	pipelineproof reproduce --output results/public

task-image:
	docker build -f docker/task.Dockerfile -t pipelineproof-task:0.3.0 .

build:
	python -m build

check: test
	pipelineproof doctor
