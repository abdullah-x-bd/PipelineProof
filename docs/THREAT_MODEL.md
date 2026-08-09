# PipelineProof threat model

PipelineProof evaluates whether a candidate repair preserves the benchmark interface while satisfying held-back machine-learning integrity checks. This threat model defines what the verifier assumes, what the candidate may attempt, and which security claims are outside scope.

## Assets protected by the benchmark

PipelineProof is designed to protect the integrity of an evaluation result, not to serve as a general-purpose hostile-code sandbox.

The relevant assets are:

1. **Held-back verifier semantics** used to distinguish genuine repairs from public-test gaming.
2. **Protected task surfaces** that define the visible benchmark contract.
3. **Private evaluation specifications and seeds** supplied to the trusted verifier outside the candidate workspace.
4. **Score integrity**, including hidden functional measurements and independent metric computation.
5. **Reproducibility metadata**, so a released score can be tied to a task, verifier, seed, and execution mode.

## Trust boundary

### Trusted

- the PipelineProof verifier process;
- private task specifications and seeds;
- the benchmark task generator;
- the independent quality evaluator;
- the Docker configuration used by the scored path;
- host-side code that launches scored execution and reads outputs;
- release evidence generated from the trusted repository revision.

### Untrusted

- candidate source code;
- model-generated patches;
- candidate runtime behaviour;
- candidate stdout and claimed success;
- candidate-side metric implementations;
- files created inside writable task surfaces;
- public tests as a complete statement of correctness.

## Candidate-visible information

A solving agent receives one task repository containing public task material:

- the issue description;
- visible data examples;
- visible tests;
- the command interface;
- the public manifest;
- writable source code.

The private evaluation specification, private seeds, held-back behavioural probes, and gold/reference repair bundle are not part of the solver workspace.

## Writable and protected surfaces

The default public task permits edits under:

```text
src/**
```

The following are protected:

```text
ISSUE.md
manifest.json
run_pipeline.py
tests/**
data/**
```

The protected-surface checker rejects modifications, unexpected additions, removals, and symlinks outside the writable source surface, subject to explicitly ignored cache artifacts.

## Threats explicitly tested

### Constant or semantically empty outputs

A candidate may return outputs of the expected type and shape without solving the hidden ML problem.

**Mitigation:** trusted functional evaluation on held-back generated data.

### Memorisation of public fixtures

A candidate may hard-code visible examples or construct behaviour conditional on public fixtures.

**Mitigation:** held-back generated data and shifted probes. The v0.4 battery repairs the historical malformed hard-coded fixture so this attack executes normally before hidden evaluation.

### Public-test conditional behaviour

A candidate may recognize public batch sizes or other visible test characteristics and behave correctly only under those conditions.

**Mitigation:** hidden evaluation uses different row counts, seeds, and transformations.

### Output-protocol forgery

A candidate may return correctly typed but invalid values such as non-finite floats.

**Mitigation:** the trusted worker requires JSON-compliant output and the verifier independently validates prediction length and finiteness. For the explicit non-finite-output attack, output rejection is the intended detector rather than an accidental fixture failure.

### Printed or self-reported success

A candidate may print plausible success text or candidate-computed metrics that do not reflect actual behaviour.

**Mitigation:** printed output is not accepted as evidence; scoring is derived from trusted execution.

### Candidate-side metric monkeypatching

A candidate may modify numerical routines used by its own evaluation code.

**Mitigation:** hidden metrics are recomputed in the trusted verifier process rather than accepting candidate-side scores as ground truth.

### Oracle import attempts

A candidate may attempt to import PipelineProof verifier logic or other oracle functionality.

**Mitigation:** scored execution is isolated from verifier internals and hidden expected values are computed outside the candidate environment.

### Protected-surface modification

A candidate may produce a correct source repair while altering the runner, tests, data, or manifest to weaken evaluation.

**Mitigation:** protected-surface hashing and path checks. The v0.4 battery applies an otherwise-correct protected edit across all six defect families so this detector is exercised independently of functional failure.

### Silent ML integrity failures

A candidate may pass visible tests while leaving one of the benchmark's target defects intact.

**Mitigation:** family-specific hidden interventions for feature ordering, preprocessing leakage, serialization state, evaluation split, group separation, and target-derived metadata.

## Execution isolation

### Local mode

Local mode is a development convenience. It applies process and resource limits but does not provide a strong filesystem or network security boundary. Local results are useful for verifier development and deterministic cross-checking.

### Docker mode

Docker is the canonical scored execution path. The current container configuration uses a read-only root filesystem and candidate mount, a separate scratch mount, no network, an unprivileged user, dropped capabilities, a process limit, CPU and memory limits, and `no-new-privileges`.

Docker materially reduces accidental cross-boundary access, but PipelineProof does not claim that a container is an absolute security boundary against arbitrary hostile code or kernel/runtime vulnerabilities.

## Threats outside scope

The current release does not claim protection against:

- Linux kernel exploits;
- Docker/container-runtime vulnerabilities;
- hardware or microarchitectural side channels;
- malicious dependencies installed before a benchmark run;
- compromise of the host running the trusted verifier;
- compromise of the model provider or agent harness;
- denial-of-service beyond configured resource/time limits;
- covert channels not represented in the benchmark interface;
- arbitrary supply-chain attacks;
- benchmark data already memorised by a future model;
- previously unknown classes of ML pipeline invalidity;
- adversaries specifically optimized against unreleased private verifier implementation details.

## Public benchmark contamination

Public development tasks are intentionally inspectable and reproducible. That means future models may eventually encounter them during training.

For consequential model comparisons, PipelineProof therefore separates the public development specification from a private evaluation bundle. Model-result reports should record the provider route, model version, harness, prompt version, and relevant environment metadata. A public development score should not be presented as contamination-resistant evidence.

## Attack-evidence validity

A rejected program is not automatically counted as a successful attack test.

The v0.4 evidence schema marks each adversarial trial as one of:

- `INVALID_ATTACK`
- `ACCEPTED_ATTACK`
- `REJECTED_ATTACK`
- `REJECTED_OTHER_CHECK`

An attack must satisfy its declared preconditions before it enters the false-accept denominator. This prevents accidental syntax errors or unrelated crashes from inflating apparent verifier robustness.

Repeated seeds are reported separately from the number of structurally distinct attack cells.

## Responsible interpretation

PipelineProof's released evidence should be phrased narrowly:

> The released verifier rejected the released valid adversarial battery and accepted the released legitimate repair controls under the reported seeds and execution configuration.

The evidence should not be summarized as "the verifier is ungameable," "PipelineProof prevents cheating," or "Docker makes arbitrary agent code safe."
