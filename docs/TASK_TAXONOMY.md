# PipelineProof task taxonomy

PipelineProof targets **silent machine-learning pipeline integrity failures**: repositories that still execute, expose the expected interface, and may pass visible tests while violating an ML-specific correctness condition.

The benchmark currently contains one public development task for each of six defect families. Each task exposes the same command surface (`train`, `predict`, `evaluate`, `split`, `features`) but the hidden verifier applies a family-specific intervention.

## Design principles

A PipelineProof defect family should satisfy four criteria.

1. **Non-crashing failure**. The broken repository should usually run and produce plausible outputs.
2. **ML-specific validity failure**. The defect should invalidate inference, evaluation, persistence, splitting, or feature construction rather than merely violate style.
3. **Executable hidden test**. The intended property must be testable from behaviour in a held-back verifier.
4. **Implementation plurality**. More than one legitimate source-level repair should be able to satisfy the behavioural contract.

## Family 1: feature-schema mismatch

**Task:** `feature-schema-a`

### Failure

The broken predictor constructs its feature matrix from record iteration order rather than the feature schema stored at training time. Semantically equivalent records can therefore produce different predictions when their keys arrive through a different schema path or order.

### Why a visible test can miss it

Visible examples may use a single stable dictionary construction order. A repair can therefore appear correct on the public fixtures while still depending on accidental ordering.

### Correct behavioural contract

- predictions remain accurate on held-back shifted rows;
- predictions are invariant to a permutation of equivalent feature-key presentation;
- serialized and reloaded state produces the same predictions;
- protected evaluation surfaces remain unchanged.

### Hidden intervention

The verifier trains on held-back rows, creates semantically identical probe rows with reversed feature-key order, round-trips the trained state, and compares normal, permuted, and reloaded predictions.

### Principal measurements

- hidden RMSE `< 0.08`;
- maximum prediction delta under key-order permutation `< 1e-9`;
- maximum reload prediction delta `< 1e-9`.

### Representative superficial repairs

- constant predictions;
- memorising public fixtures;
- behaving correctly only for the public batch shape;
- spoofing success output;
- attempting verifier-oracle access;
- monkeypatching candidate-side metric code.

---

## Family 2: evaluation leakage during preprocessing

**Task:** `preprocessing-eval-a`

### Failure

The broken training procedure fits preprocessing statistics using both training and evaluation rows. The trained artifact therefore changes when only the evaluation distribution changes.

### Why a visible test can miss it

The pipeline can produce low error and run cleanly even when evaluation data influenced the fitted transformation. Ordinary example-based tests may verify only output shape or basic prediction quality.

### Correct behavioural contract

- preprocessing is fitted only on training rows;
- changing held-out evaluation rows does not change the trained artifact;
- predictions remain accurate on shifted held-back rows;
- serialization preserves predictions.

### Hidden intervention

The verifier trains twice on identical training data but two different evaluation sets, then compares the resulting artifacts and evaluates a shifted hidden probe set.

### Principal measurements

- hidden RMSE `< 0.08`;
- training artifact exactly invariant to evaluation-set substitution;
- reload prediction delta `< 1e-9`.

---

## Family 3: missing preprocessing state after serialization

**Task:** `serialization-a`

### Failure

The broken artifact stores the predictive model but omits preprocessing state. At serving time, preprocessing statistics are recomputed from the current batch, so a prediction can change depending on which other records happen to be served alongside it.

### Why a visible test can miss it

A fixed evaluation batch can look correct. The bug appears only when batch composition changes or when the persisted artifact is used in a different serving context.

### Correct behavioural contract

- all inference-time preprocessing state required by the model is persisted;
- the same record receives the same prediction alone or inside a different batch;
- predictions remain accurate after serialization.

### Hidden intervention

The verifier round-trips the state, predicts one record alone, then predicts the same record as part of a rearranged batch.

### Principal measurements

- hidden RMSE `< 0.08`;
- batch-composition prediction delta `< 1e-9`;
- persistence uses the same batch-composition invariant.

---

## Family 4: evaluation on the wrong split

**Task:** `wrong-eval-a`

### Failure

The broken evaluator reports performance on training rows instead of the held-out evaluation rows supplied through the interface.

### Why a visible test can miss it

The evaluation command still returns a plausible numeric metric. Without an independent recomputation, a caller may accept a systematically optimistic or simply irrelevant score.

### Correct behavioural contract

- the reported metric is computed on the supplied evaluation rows;
- the candidate's reported RMSE agrees with an independently computed trusted RMSE;
- predictions on held-back evaluation rows remain accurate.

### Hidden intervention

The verifier independently predicts the held-out evaluation set, computes its own RMSE, invokes the candidate's evaluation routine, and compares the two values.

### Principal measurements

- hidden prediction RMSE `< 0.08`;
- reported RMSE is finite;
- absolute difference between reported and trusted RMSE `< 1e-9`.

---

## Family 5: group leakage across splits

**Task:** `group-leakage-a`

### Failure

The broken splitter shuffles individual rows and can place records from the same group on both sides of the train/evaluation boundary.

### Why a visible test can miss it

Both splits can have the expected sizes and contain all rows while still leaking related units across the evaluation boundary.

### Correct behavioural contract

- every input row appears exactly once across the two splits;
- the train fraction remains within a practical range;
- no group identifier appears in both train and evaluation;
- repeated splitting with the deterministic benchmark seed is stable.

### Hidden intervention

The verifier supplies grouped rows, runs the split operation twice, checks row coverage and ratio, measures group overlap, and tests deterministic equality.

### Principal measurements

- exact row coverage with no duplication;
- train ratio between `0.55` and `0.90`;
- group overlap `== 0`;
- repeated split outputs exactly equal.

---

## Family 6: target-derived feature leakage

**Task:** `target-leakage-a`

### Failure

The broken feature builder includes `target_proxy`, a field derived from evaluation-only target information, in the model input.

### Why a visible test can miss it

The leaked feature can improve apparent predictive performance. Tests that look only at accuracy can therefore reward the invalid pipeline.

### Correct behavioural contract

- neither `target` nor `target_proxy` appears in the feature schema;
- perturbing target-only metadata at evaluation time does not change predictions;
- predictions remain accurate using legitimate features alone.

### Hidden intervention

The verifier creates a shifted hidden probe set, then creates a second copy with both target and target-proxy metadata shifted by a large amount. It compares predictions and inspects the declared feature columns.

### Principal measurements

- hidden RMSE `< 0.08`;
- maximum prediction change after target-metadata perturbation `< 1e-9`;
- feature columns exclude both `target` and `target_proxy`.

---

## Shared protected surface

Across all six families, agents may edit only files under `src/**`. The benchmark treats the following surfaces as protected:

- `ISSUE.md`
- `manifest.json`
- `run_pipeline.py`
- `tests/**`
- `data/**`

The verifier hashes the baseline protected surface and rejects added, removed, changed, or symlinked protected content. This is not a complete security boundary; it is an integrity rule for the benchmark task.

## Current scope

The released development suite contains six compact deterministic tasks. They are designed to isolate verifier semantics and make attack/repair auditing tractable. They are not claimed to represent the full distribution of production ML failures, and they do not yet include a frontier-model leaderboard.
