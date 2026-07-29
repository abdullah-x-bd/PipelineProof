#!/usr/bin/env sh
set -eu
docker build -f docker/task.Dockerfile -t pipelineproof-task:0.3.0 .
