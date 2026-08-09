# Contributing

PipelineProof is a research benchmark, so changes are evaluated for measurement validity as well as software correctness.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
ruff check .
pytest
pipelineproof doctor
```

Windows PowerShell activation:

```powershell
.venv\Scripts\Activate.ps1
```

The supported Python matrix is 3.11 through 3.13.

## Pull requests

Keep each pull request focused. Describe:

- the benchmark or software problem being changed;
- the behavioural invariant affected;
- tests added or changed;
- whether the attack battery, valid-control set, reward, evidence schema, or task semantics change;
- whether canonical evidence must be regenerated.

Do not commit private evaluation specifications, private seeds, unpublished model-provider credentials, or agent-accessible gold repairs.

## Adding or changing a task family

A task-family change should include:

1. A concrete silent ML failure mechanism.
2. A public symptom that does not reveal the hidden oracle.
3. A hidden behavioural or causal contract.
4. At least one broken control.
5. Multiple behaviourally correct repair implementations when practical.
6. A held-back intervention that distinguishes superficial repair from genuine repair.
7. Thresholds justified by the task construction rather than selected after seeing a model leaderboard.
8. Documentation in `docs/TASK_TAXONOMY.md` and `docs/VERIFIER_SPEC.md`.
9. Tests covering the broken and valid controls.
10. Regenerated canonical evidence if released benchmark behaviour changes.

## Verifier changes

Verifier changes require extra scrutiny. A change should not be accepted merely because it rejects more attacks. Check both directions:

- false acceptance of valid adversarial attempts;
- false rejection of legitimate repairs.

Every new released attack must define its validity preconditions and intended detector. Malformed attacks must not be counted as verifier-soundness evidence.

## Adversarial battery changes

For each new structural attack, record:

- attack ID;
- category;
- target task;
- attack rationale;
- conditions that make the attack valid;
- intended verifier detector;
- expected outcome.

Seed repetitions are repetitions, not new structural attacks.

## Reward changes

Any reward-weight or gating change must update `docs/REWARD_SPEC.md` and preserve a tested progression from clearly invalid candidates toward complete repair. Report a reward change as a benchmark-semantic change, not a refactor.

## Evidence changes

Canonical evidence is generated through Docker. Run:

```bash
python scripts/reproduce_release.py --output results/reproduced/v0.4.0 --seeds 4
```

Then validate with:

```bash
pipelineproof validate-evidence --input results/reproduced/v0.4.0
```

Do not hand-edit canonical measurements. Environment metadata may be augmented by the release workflow only with execution facts such as the Docker image ID, after which the evidence manifest must be regenerated.

## Model evaluation

Real model rollouts must use the schema in `docs/MODEL_EVALUATION.md` and `schemas/model-rollout.schema.json`. Record exact model/version identifiers, provider route, harness, task, rollout ID, reward, independent quality, and failure class.

Synthetic fixtures must be unmistakably labelled and must never be presented as empirical leaderboard results.

## Style

- Ruff is the source-code style gate.
- Public functions should have clear type annotations.
- Prefer behavioural tests over implementation-specific assertions.
- Avoid comments that merely restate the code.
- Keep generated evidence out of source hashes and source code out of generated evidence directories.

## Release changes

Follow `docs/RELEASE_PROCESS.md`. A release is not complete until package tests, Docker execution, evidence validation, provenance checks, and the release audit are all green.
