# Environment card

## Capability

Repair a runnable ML repository whose output is plausible but violates a data, evaluation, or serving contract.

## Agent input

The agent receives one repository and one issue description. It may edit `src/**` only.

## Agent output

A patched repository.

## Verification

The verifier checks:

- Command interface
- Public tests
- Hidden functional accuracy
- Family-specific causal intervention
- State persistence or determinism
- Protected-file integrity

The verifier scores behaviour. It does not compare against a gold patch or trust stdout.

## Reward

| Component | Weight |
|---|---:|
| Interface | 0.10 |
| Public tests | 0.10 |
| Hidden functional correctness | 0.25 |
| Causal contract | 0.35 |
| Persistence or determinism | 0.10 |
| Protected surface | 0.10 |

Causal and persistence reward are available only when hidden functional correctness passes.

## Splits

The public repository contains six development tasks. The separate private bundle contains six evaluation tasks with different schemas, seeds, and repository structure.

## Claims

PipelineProof demonstrates a working task, verifier, controls, attack battery, and reproducibility layer. It does not yet establish frontier-model separation or transfer from RL training.
