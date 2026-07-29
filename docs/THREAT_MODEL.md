# Threat model

## Trust boundary

Trusted:

- Task specification with oracle parameters
- Verifier process
- Independent quality suite
- Private seeds
- Gold and alternative repairs

Untrusted:

- Agent-generated code
- Candidate stdout and exit claims
- Candidate artifacts
- Added files
- Reported metrics

## Attacks covered

- Constant output
- Hardcoded public examples
- Non-finite output with valid shape
- Fake success text
- Public-test-specific branch
- Import of verifier internals
- Trusted-metric monkeypatch
- Protected-file modification
- Additional files outside the writable surface
- Symlinks outside the intended surface

## Isolation

Docker mode uses a read-only root filesystem, no network, a read-only candidate mount, a separate scratch mount, an unprivileged user, dropped capabilities, a process limit, CPU and memory limits, and `no-new-privileges`.

Local mode is not a security boundary. It is retained for free development and deterministic evidence generation. Docker execution remains required before a scored external run.

## Residual risks

- A candidate may identify the form of public verifier interventions.
- The attack battery is finite.
- Docker was not available in the build host used for the committed local evidence.
- The current tasks use small linear models and do not establish transfer to large training pipelines.
- Repeated seed trials over one structural task are correlated.
