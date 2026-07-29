# Environment specification

## Capability target

PipelineProof measures whether a coding agent can diagnose and repair non-crashing defects that invalidate a machine-learning pipeline while preserving its public interface.

A successful repair must restore the intended behavioural contract. The environment does not require similarity to a canonical patch and does not trust metrics or success claims emitted by agent-controlled code.

## Integrity contracts

### Training-data provenance

Only information legitimately assigned to training may influence fitted state. Evaluation rows, evaluation labels, protected group copies, and target-derived features must not enter fitting or model selection through an unauthorized path.

### Evaluation validity

The reported score must be computed on the intended held-out population, against the intended target representation, with the intended metric semantics. Training performance or a malformed proxy must not substitute for held-out evaluation.

### Train-serving equivalence

A clean inference process must apply the same feature schema, transformations, units, and model artifact semantics established during training.

## Agent surface

Each task declares a narrow writable surface, expected initially to include `src/**` and selected configuration files. Public tests, data, package metadata, and verifier material are protected.

The sandbox must enforce these boundaries. Instructions alone are not a security control.

## Verification architecture

The target architecture separates solving from scoring:

1. An agent receives a task workspace containing only public assets.
2. The agent modifies permitted files and produces a patch snapshot.
3. The snapshot is copied into a fresh verifier runtime.
4. The trusted verifier generates secret interventions outside the agent process.
5. Independent checks score behavioural contracts, regressions, reproducibility, and policy compliance.

## Initial task families

The intended first six families are:

1. Preprocessing fitted on evaluation data
2. Group leakage across train and evaluation splits
3. Target-derived feature leakage
4. Evaluation performed on the wrong split
5. Feature-schema or feature-order mismatch
6. Missing or inconsistent preprocessing serialization

The first implemented vertical slice will be feature-schema mismatch because it supports cheap, deterministic, patch-independent metamorphic verification.

## Reward direction

The first reward should be graded across independently testable properties:

- Public interface and regression behaviour
- Hidden functional correctness
- Relevant integrity-contract checks
- Train-serving equivalence
- Reproducibility
- Protected-file compliance

The exact weights will be frozen only after the first honest-control and cheat-battery experiments. Reward weights must not be chosen merely to make a preferred model ranking appear clean.
