# PipelineProof reward specification

PipelineProof exposes both a strict binary pass and a graded reward. The graded reward is intended for RL-style training, search analysis, and partial-repair diagnostics. It must not be confused with benchmark success.

## Components

For Boolean indicators interpreted as zero or one:

| Symbol | Check | Weight |
|---|---|---:|
| `I` | command interface is valid | 0.10 |
| `P` | public tests pass | 0.10 |
| `F` | hidden functional correctness | 0.25 |
| `C` | family-specific causal / integrity contract | 0.35 |
| `S` | persistence / repeatability contract | 0.10 |
| `G` | protected evaluation surface unchanged | 0.10 |

The raw conceptual sum is one, but the causal and persistence components are gated by functional correctness.

```text
R = 0.10 I
  + 0.10 P
  + 0.25 F
  + 0.35 (C AND F)
  + 0.10 (S AND F)
  + 0.10 G
```

The implementation rounds the total to six decimal places.

## Why causal and persistence reward are gated

An earlier verifier version treated invariance as independently rewardable. That produced a pathological incentive: a constant predictor is highly invariant and perfectly repeatable even though it does not solve the ML task.

PipelineProof therefore gives causal and persistence credit only after the hidden functional check passes. This makes invariance a property of a working solution rather than a substitute for one.

## Binary pass rule

A candidate passes only when:

```text
interface == true
public_tests == true
functional == true
causal == true
persistence == true
protected == true
reward.total == 1.0
```

A high partial score is never converted into a benchmark pass.

## Canonical reward ladder

The release evidence intentionally evaluates five qualitatively different repair states on the feature-schema task.

| Level | Intended interpretation |
|---|---|
| invalid interface | source cannot provide the required command contract |
| format-only success | repository looks executable and passes weak visible checks but is functionally wrong |
| unrepaired repository | pipeline remains usable and partly functional but violates the hidden ML contract |
| correct repair with protected edit | ML behaviour is correct, but benchmark integrity has been tampered with |
| complete repair | all hidden, public, persistence, and integrity conditions hold |

The evidence generator asserts strict monotonicity of the observed total reward across these five levels. A monotonicity failure is treated as evidence-design regression rather than merely a cosmetic reporting issue.

## Interpretation by task family

The numerical weights remain fixed across families, but the meaning of `F`, `C`, and `S` is family-specific. See `docs/VERIFIER_SPEC.md` for the exact interventions and thresholds.

This design intentionally makes the benchmark score comparable at the level of verifier dimensions while allowing the hidden integrity contract to reflect the underlying ML failure.

## Independent quality score

PipelineProof also contains a separate quality evaluator used for analyses such as labelled candidate search and model-report best-of-N curves. The independent quality score is not substituted for the verifier reward and is read only after candidate selection in best-of-N reporting.

This separation is intended to reduce a common evaluation failure mode in which the same noisy proxy both selects and judges candidate solutions.

## Claim boundary

The current weights are a benchmark design choice, not an empirically calibrated statement that causal correctness is exactly 3.5 times as valuable as interface validity in production ML systems.

The release validates ordering and gating properties of the reward on the benchmark controls. It does not claim that the weighting is universally optimal for reinforcement learning or economic utility.
