# Trusted verifier specification

This document describes the behavioural checks implemented by PipelineProof's trusted verifier. It is intended to make the benchmark contract inspectable without requiring a reader to infer semantics from source code.

## Verification result

Every candidate is evaluated along six Boolean dimensions:

1. `interface`
2. `public_tests`
3. `functional`
4. `causal`
5. `persistence`
6. `protected`

A candidate passes only if **all six checks are true** and the weighted reward is exactly `1.0`.

The family-specific definitions of `functional`, `causal`, and `persistence` differ by defect family. `interface`, `public_tests`, and `protected` are shared.

## Shared checks

### Interface

The verifier runs:

```bash
python -I run_pipeline.py --help
```

The check passes when the command exits successfully. The isolated-Python flag reduces dependence on the invoking Python environment.

This check establishes only that the expected command surface can be imported and invoked. It does not establish semantic correctness.

### Public tests

The verifier runs:

```bash
python -m pytest -q tests
```

The check passes when the visible repository tests pass.

Public tests are intentionally insufficient for the complete task. PipelineProof is specifically designed around failures that can survive visible tests while violating an ML-specific hidden contract.

### Protected surface

The candidate workspace is compared with a fresh broken-task baseline. Files under `src/**` are writable. Other task surfaces are protected.

The protected check fails for:

- a modified protected file;
- an added file outside the writable source surface;
- a missing protected file;
- a symlink on a protected or unexpected surface.

Cache files such as Python bytecode and test caches are ignored.

This check protects benchmark integrity. It is not intended as a complete sandbox or host-security mechanism.

## Feature-schema verifier

### Hidden data

- 80 generated training rows;
- 24 shifted probe rows with target metadata stripped;
- a semantically identical copy of the probe rows with feature-key presentation reversed.

### Operations

The candidate is asked to:

1. train;
2. serialize and reload state;
3. predict the ordinary probe;
4. predict the reloaded probe;
5. predict the key-order-permuted probe.

### Functional check

Trusted hidden RMSE against the benchmark data-generating process must satisfy:

```text
RMSE < 0.08
```

### Causal check

Equivalent records must be invariant to feature-key presentation:

```text
max |prediction_normal - prediction_permuted| < 1e-9
```

### Persistence check

Round-tripped state must preserve predictions:

```text
max |prediction_original - prediction_reloaded| < 1e-9
```

## Preprocessing/evaluation-leakage verifier

### Hidden data

- 80 training rows;
- two distinct 30-row evaluation sets;
- 20 shifted hidden probe rows.

### Operations

The candidate is trained twice on exactly the same training rows but with different evaluation distributions. One resulting state is serialized and reloaded. Predictions are produced on the same hidden probe.

### Functional check

```text
hidden RMSE < 0.08
```

### Causal check

The complete trained artifact must be exactly invariant to substitution of the evaluation set:

```text
json.dumps(state_a, sort_keys=True) == json.dumps(state_b, sort_keys=True)
```

This operationalizes the intended rule that evaluation data must not affect fitted preprocessing or model state.

### Persistence check

```text
max |prediction_original - prediction_reloaded| < 1e-9
```

## Serialization verifier

### Hidden data

- 80 training rows;
- 7 shifted probe rows.

### Operations

The trained state is serialized and reloaded. One probe row is predicted alone and again as part of a rearranged mixed batch.

### Functional check

```text
hidden RMSE < 0.08
```

### Causal check

The prediction for the same record must not depend on unrelated batch companions:

```text
batch_composition_delta < 1e-9
```

### Persistence check

The same batch-composition condition is used as the persistence criterion because the family is specifically designed to detect omitted serving-time preprocessing state after a round trip.

## Wrong-evaluation-split verifier

### Hidden data

- 70 training rows;
- 25 shifted evaluation rows.

### Operations

The verifier obtains predictions on the evaluation rows, independently calculates RMSE, and separately calls the candidate's `evaluate` operation using both train and evaluation data.

### Functional check

```text
hidden prediction RMSE < 0.08
```

### Causal check

The reported metric must be finite and agree with the trusted evaluation-set RMSE:

```text
abs(reported_rmse - trusted_rmse) < 1e-9
```

### Persistence check

The reported RMSE must be finite.

## Group-leakage verifier

### Hidden data

- 90 generated rows carrying `row_id` and `group_id` metadata.

### Operations

The same deterministic split is requested twice.

### Functional check

The split must preserve exact row coverage and a reasonable train fraction:

```text
all rows represented exactly once
0.55 <= train_fraction <= 0.90
```

### Causal check

No group may occur on both sides:

```text
train_groups ∩ eval_groups == ∅
```

### Persistence check

Repeated splitting with the same task seed must return exactly the same result.

## Target-derived-feature verifier

### Hidden data

- 80 training rows;
- 20 shifted probe rows;
- a copy of the probe with `target` and `target_proxy` shifted by `+500`.

### Operations

The candidate is trained and round-tripped, then asked to predict both metadata variants and expose its feature-construction output.

### Functional check

```text
hidden RMSE < 0.08
```

### Causal check

Both conditions must hold:

```text
max |prediction_original - prediction_target_shifted| < 1e-9
```

and the declared feature columns must exclude both:

```text
target
target_proxy
```

### Persistence check

This family currently sets persistence to true once the operation path completes. Persistence-specific corruption is tested in the serialization family.

## Reward semantics

The verifier exposes a graded reward for training and RL-style use. Passing remains stricter than obtaining partial reward.

| Check | Weight |
|---|---:|
| Interface | 0.10 |
| Public tests | 0.10 |
| Functional hidden correctness | 0.25 |
| Causal / integrity contract | 0.35 |
| Persistence | 0.10 |
| Protected surface | 0.10 |

The `causal` and `persistence` contributions are **gated on functional correctness**. A candidate that produces a constant output can be invariant and repeatable, but those properties do not earn causal or persistence reward unless the candidate is functionally correct.

Formally, with Boolean checks interpreted as zero or one:

```text
R = 0.10 I
  + 0.10 P_public
  + 0.25 F
  + 0.35 (C ∧ F)
  + 0.10 (S ∧ F)
  + 0.10 P_protected
```

A benchmark pass requires:

```text
all checks == true
and
R == 1.0
```

## Adversarial validation

The v0.4 evidence battery does not count every rejected program as evidence of verifier soundness.

Each attack has:

- a structural attack identifier;
- a target task;
- an attack category;
- required preconditions;
- an intended verifier check;
- repeated seed trials.

A malformed attack fixture is marked `INVALID_ATTACK` and excluded from the false-accept denominator. A valid attack is reported as:

- `ACCEPTED_ATTACK` if the verifier passes it;
- `REJECTED_ATTACK` if the intended detector fires;
- `REJECTED_OTHER_CHECK` if it is rejected, but not by the intended path.

The non-finite-output attack is a deliberate protocol attack. For that case, failure of finite JSON output is the intended detector rather than an accidental fixture failure.

## Valid-repair validation

The release carries three independent legitimate repair styles per family:

- `canonical`
- `alternative`
- `refactor`

Across six families, this produces 18 structural valid-repair cells. Repeated seeds are reported separately. The benchmark therefore tests behavioural acceptance of multiple implementations instead of validating only one author-preferred patch.

## Execution modes

### Local mode

Local mode provides process and resource limits and is intended for development, debugging, and fast reproduction. It does not provide filesystem or network isolation equivalent to the scored container path.

### Docker mode

Docker is the canonical scored execution mode. The container configuration uses a read-only candidate mount, dropped capabilities, explicit CPU and memory limits, and the benchmark network-isolation policy.

The v0.4 evidence workflow runs the full attack and valid-control battery through Docker and separately compares a structural local/Docker parity pass.

## Claim boundary

A clean released battery supports this claim:

> Under the released task set, attack constructions, seeds, and execution configuration, the verifier accepted the released valid repairs and rejected the released adversarial battery through the reported checks.

It does **not** prove universal soundness against arbitrary programs, sandbox escapes, undiscovered verifier weaknesses, future benchmark contamination, or every production ML failure mode.
