# PipelineProof full build plan

## Objective

Deliver one small, complete, defensible RL environment that Tensium can install, run, attack, and reproduce. The environment will test whether coding agents repair silent machine-learning pipeline integrity failures rather than merely make visible tests pass.

The build is governed by evidence gates. We do not expand task volume until the current layer is shown to measure what it claims.

## Definition of done

The trial submission is complete when it contains:

- An installable wheel exposing `load_environment`
- Original public tasks with clean train, development, and evaluation boundaries
- A solving sandbox with declared resource and network policy
- A trusted verifier whose hidden assets are unavailable to the agent
- Gold and alternative correct solutions
- A versioned adversarial cheat battery
- False-accept and false-reject estimates with 95 percent confidence intervals
- A graded reward with a demonstrated capability ladder
- A reproducible model panel with uncertainty and failure classification
- A best-of-N reward-hacking check against an independent quality suite
- A reproducibility bundle that regenerates every reported table and figure
- A short reasoning document covering role fit, capability choice, contamination, attacks, mistakes, limitations, and comments on the Tensium template

## Scope discipline

The first submission will be repository-level and single-task-per-rollout. It will not be described as long-horizon unless it later satisfies Tensium's causal-step, heterogeneous-tool, persistent-state, and failure-recovery requirements.

The first release targets six defect families and approximately twelve structurally distinct tasks. Generated renamings do not count as distinct tasks.

## Stage 0. Repository foundation

### Work

- Establish the Python package and `load_environment` interface
- Add CI across supported Python versions
- Add a Docker build baseline
- Define public and private asset boundaries
- Add linting and tests
- Record major design decisions in version control

### Exit gate

A fresh checkout installs successfully, `pytest` passes, `pipelineproof doctor` exits successfully, and no protected material is committed.

## Stage 1. Research framing and threat model

### Work

- Write a narrow benchmark landscape covering ML debugging, repository repair, silent training errors, invariant checking, mutation testing, and ML-agent benchmarks
- Specify what existing work measures and what PipelineProof adds
- Define the agent, verifier, task-author, and attacker trust boundaries
- Enumerate likely reward attacks before implementing the verifier
- Define claims we will not make, including unsupported priority claims such as “first benchmark”

### Outputs

- `docs/RELATED_WORK.md`
- `docs/THREAT_MODEL.md`
- Versioned attack taxonomy

### Exit gate

The project has one precise capability claim, one practical user story, and an explicit account of the closest substitutes.

## Stage 2. Formal task and reward contract

### Work

- Define the task manifest schema
- Define writable and protected paths
- Define execution commands, timeout, resource limits, and expected outputs
- Define public checks and hidden checks
- Define the reward-component interface without fixing arbitrary weights prematurely
- Define what constitutes a valid alternative solution
- Define task-family clustering for statistical analysis

### Outputs

- Machine-readable task schema
- Environment contract tests
- Draft reward card

### Exit gate

A competent engineer can implement a task and a verifier from the specification without guessing the intended behaviour.

## Stage 3. First complete vertical slice

### Chosen family

Feature-schema mismatch between training and inference.

### Why first

- Non-crashing and behaviourally meaningful
- Cheap and deterministic to execute
- Supports several correct repair strategies
- Supports strong metamorphic tests
- Does not require expensive model training

### Task construction

Create one original repository where:

- Training selects named features in one order
- Inference constructs a numerically valid array in a different order
- The pipeline runs and emits plausible predictions
- Public tests check only interface and simple examples
- The issue description identifies symptoms without revealing the defect

### Required controls

- Canonical correct repair
- At least two structurally different correct repairs
- Constant-output cheat
- Hardcoded-visible-example cheat
- Output-shape forgery
- Fake-success stdout
- Public-test-specific conditional
- Attempted modification of protected files

### Exit gate

The verifier accepts all labelled correct repairs, rejects the initial cheat set, and produces a useful graded distinction between untouched, partial, and complete solutions.

## Stage 4. Trusted verifier and hidden interventions

### Work

- Run scoring outside the agent-controlled process
- Generate secret inference rows after the agent finishes
- Test invariance to named-column permutation
- Test persistence across save, process termination, and reload
- Validate numerical finiteness, schema, and row identity
- Hash protected files before and after the rollout
- Prevent import shadowing and agent-controlled metric substitution
- Separate reward tests from the independent quality suite

### Architecture

```text
agent workspace -> patch snapshot -> fresh verifier runtime -> secret interventions -> score
```

### Exit gate

The agent workspace cannot read or import the oracle, private seeds, independent quality suite, or trusted scoring implementation. An automated isolation test proves the boundary.

## Stage 5. Sandbox baseline

### Work

- Run untrusted code in Docker initially
- Use an unprivileged user
- Set wall-clock timeout, memory limit, CPU limit, process limit, and writable-directory restrictions
- Disable network egress for scored runs
- Terminate the full process group on timeout
- Record image digest and runtime manifest
- Keep trusted verification in a separate runtime

### Exit gate

Sandbox behaviour is reproducible, declared in a checked-in manifest, and tested against path traversal, background processes, fork attempts, and network access.

## Stage 6. Soundness receipt for the vertical slice

### Work

Create labelled corpora of invalid and valid solutions.

Invalid classes must include at least:

- Memorised or hardcoded answers
- Constant output
- Output-shape forgery
- Reading or importing references

Additional classes should include:

- Monkeypatching the metric
- Test-runner replacement
- Hidden-input detection
- Numerical-tolerance exploitation
- Cached cross-run state
- Exit-code and stdout forgery

Valid controls must include:

- Minimal patch
- Pipeline-based repair
- Explicit schema-validation repair
- Broader refactor preserving the contract

### Analysis

- Compute observed false-accept and false-reject rates
- Report Wilson 95 percent confidence intervals
- Name every surviving attack
- Version the cheat battery

### Exit gate

No result is described as an absolute verifier property. Reports identify the verifier version, attack-battery version, labelled sample counts, and intervals.

## Stage 7. Expand to six defect families

Implement in this order:

1. Feature-schema mismatch
2. Preprocessing fitted on evaluation data
3. Missing preprocessing serialization
4. Evaluation on the wrong split
5. Group leakage across splits
6. Target-derived feature leakage

For each family:

- Start with one hand-authored vertical slice
- Create multiple correct implementations
- Attack the family-specific verifier
- Add a second structurally different repository only after soundness tests pass
- Record the causal contract and the intervention that tests it

### Exit gate

Every family has at least two structurally distinct tasks, at least two accepted correct-repair styles, family-specific attacks, and an independent quality check.

## Stage 8. Dataset design and contamination controls

### Splits

- Development tasks may be public
- Final evaluation tasks and seeds remain held back
- Repository structures, data schemas, and defect locations differ across splits
- A family may appear across splits, but exact repository templates must not

### Provenance

Record for each task:

- Generator or author version
- Creation timestamp
- Source rationale
- Template-family identifier
- Public-data source where applicable
- Dataset hash
- Repository hash
- Canary identifier stored outside the agent surface

### Statistical unit

Generated instances from one template are correlated. Report both:

- Instance-micro scores
- Family-macro scores

Use defect family or structural template as the resampling cluster for headline confidence intervals.

### Exit gate

A sceptical reviewer can trace every task to original work or a named public source and can see why the exact task was not likely present in model training data.

## Stage 9. Graded reward and capability ladder

### Work

Freeze reward components only after observing honest and adversarial controls.

Candidate components:

- Public interface and regression behaviour
- Hidden functional correctness
- Training-provenance contract
- Evaluation-validity contract
- Train-serving-equivalence contract
- Reproducibility
- Protected-file compliance

Construct a labelled ladder:

1. Untouched broken repository
2. Cosmetic or stdout-only change
3. Visible-test overfit
4. Partial causal repair
5. Complete repair with a regression
6. Complete contract-preserving repair

### Exit gate

Reward increases monotonically across the ladder, has useful resolution, does not saturate across the initial model panel, and correlates with independent quality.

## Stage 10. Model panel and measurement hygiene

### Model evaluation record

For every rollout, store:

- Exact model and version
- Provider route
- Harness or scaffold
- Prompt version
- Temperature and sampling settings where exposed
- Turn and token limits
- Sandbox manifest version
- Task and verifier version
- Start and end status
- Raw patch and trajectory reference
- Reward components
- Independent quality score where applicable
- Failure class

### Analysis

- Use repeated rollouts where variance requires them
- Report task-level and family-level uncertainty
- Rank models by a lower confidence bound, not only mean score
- Use paired or clustered bootstrap comparisons
- Disclose scaffold and route effects

### Exit gate

At least three meaningfully different capability levels are separated, or the report honestly concludes that the environment does not yet separate the tested panel.

## Stage 11. Reward-hack resistance under search

### Work

Run best-of-N at increasing search budgets, initially N = 1, 2, 4, and 8 where cost permits.

For each task and budget:

- Select the attempt with highest verifier reward
- Evaluate it on the independent quality suite
- Plot reward and independent quality together
- Inspect newly discovered exploit patterns
- Add confirmed exploits to the next cheat-battery version

### Exit gate

Verifier reward does not systematically climb while independent quality remains flat. If it does, repair the verifier before submission.

## Stage 12. Stability, variance, and failure taxonomy

### Failure classes

- Genuine capability limitation
- Defect located, repair incorrect
- Visible symptom fixed, causal violation remains
- Public-test overfit
- Regression introduced
- Protected-surface violation
- Timeout or resource exhaustion
- Sandbox or dependency defect
- Verifier defect
- Task ambiguity
- Harness or orchestration defect
- Ambiguous, requires human review

### Work

- Estimate variance by model, task, family, and scaffold
- Identify tasks dominating uncertainty
- Concentrate reruns on high-variance cells
- Treat flaky tests as environment defects until demonstrated otherwise

### Exit gate

Every headline interval states its rollout count and clustering method. High-variance tasks are explained, repaired, or excluded with a recorded reason.

## Stage 13. Reproducibility and packaging

### Work

- Build and install the wheel in a clean environment
- Pin or record dependency versions
- Save the Docker image digest
- Provide one-command gold, cheat, evaluation, and report regeneration paths
- Store public aggregate results and hashes of private result bundles
- Add CI for package, tests, isolation checks, and reproducibility smoke tests

### Intended commands

```bash
python -m build
pipelineproof generate --split development --seed-manifest manifests/dev.json
pipelineproof verify --task TASK_ID --candidate PATH
pipelineproof run-cheats --battery attacks/v1
pipelineproof soundness-report --input results/raw --output results/public
pipelineproof leaderboard --manifest manifests/model-panel.json
pipelineproof reproduce --manifest manifests/release.json
```

These commands are targets. They must not be documented as working until implemented and tested.

### Exit gate

A fresh machine can regenerate every public claim from the release manifest and the separately supplied private evaluation bundle.

## Stage 14. Tensium reasoning document

Write the short document from completed evidence, not from intention.

Required sections:

1. Short bio, current abilities, and concrete gaps
2. Builder and build-lead role fit
3. Targeted frontier-model weakness and baseline evidence
4. Task provenance and contamination argument
5. Verifier attacks, results, and surviving weaknesses
6. One design decision that was wrong and how it changed
7. Results, uncertainty, and failure taxonomy
8. Limitations and transfer claims not established
9. Comments on the Tensium template

Potential template comments to test through the build:

- False-accept rate depends on a defined attack distribution and verifier version
- Generated instances require clustered uncertainty estimates
- Hidden-test secrecy and agent-runtime isolation are related but distinct claims
- A leaderboard can measure scaffold capability as much as model capability unless both are varied

## Stage 15. Final submission audit

Before submission, verify:

- Every README command works exactly as written
- No private key, seed, oracle, or credential appears in Git history
- The wheel installs in a clean environment
- Gold and alternative correct solutions pass
- Every cheat class has recorded outcomes
- False-accept and false-reject intervals regenerate
- Model panel results regenerate
- Best-of-N and independent-quality curves regenerate
- Raw failure classifications are reviewable
- Limitations are explicit
- Claims match the evidence and avoid unsupported novelty language

## Immediate next milestone

Build the first feature-schema-mismatch task as a complete vertical slice. Do not add a second defect family until this milestone has:

- One broken but runnable repository
- One issue instruction
- Public tests
- Secret metamorphic inputs
- A canonical repair
- Two alternative correct repairs
- At least six adversarial cheats
- A trusted verifier
- A Docker execution path
- A first false-accept and false-reject report
