FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN python -m pip install --upgrade pip && \
    python -m pip install "numpy>=1.26" "pytest>=8.3"

COPY src/pipelineproof/_worker.py /opt/pipelineproof/worker.py

USER 65532:65532
WORKDIR /workspace
