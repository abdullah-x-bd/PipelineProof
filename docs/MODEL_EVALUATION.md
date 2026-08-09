# Model evaluation

PipelineProof does not call model providers directly. A harness writes one JSON object per rollout to a JSONL file. The machine-readable record shape is documented in `schemas/model-rollout.schema.json` and enforced by the loader used by `pipelineproof model-report`.

Required fields:

```json
{
  "model": "provider-model-version",
  "provider_route": "direct",
  "harness": "terminal-agent",
  "task_id": "feature-schema-a",
  "rollout_id": "0001",
  "reward": 0.85,
  "passed": false,
  "independent_quality": 0.90,
  "failure_class": "partial_repair"
}
```

`reward` and `independent_quality` must be between zero and one. Rollout identifiers must be unique within each model, route, harness, and task cell. Numeric identifiers define best-of-N generation order.

Optional fields may include the model endpoint, prompt version, token limits, turn limit, sandbox image digest, trajectory path, patch path, latency, token counts, and cost.

For consequential comparisons, record enough metadata to reconstruct the actual evaluation condition. At minimum, prefer an immutable model/version identifier where the provider exposes one, the exact PipelineProof commit, Docker image digest, prompt/harness version, task set, rollout budget, and any provider-side sampling parameters.

Generate the report with:

```bash
pipelineproof model-report \
  --input results/model-rollouts.jsonl \
  --output results/model-report
```

The output contains:

- `model_panel.json`
- `best_of_n.json`
- `failure_breakdown.json`

The panel groups results by model, provider route, and harness. Repeated rollouts are averaged within task before confidence intervals are estimated. Cells are ranked by the lower bound of the task-clustered reward interval. Pairwise differences use tasks shared by both cells. The best-of-N report selects the highest verifier reward within each search budget before reading independent quality.

## Synthetic reporting fixture

`examples/model_rollouts.synthetic.jsonl` exists only to exercise the reporting path. Its model names and provider route are explicitly synthetic/fixture values. It is not empirical evidence and must never be copied into a leaderboard, abstract, paper result table, or model-performance claim.

A smoke report can be generated with:

```bash
pipelineproof model-report \
  --input examples/model_rollouts.synthetic.jsonl \
  --output /tmp/pipelineproof-model-report
```

## Reporting real model results

Separate verifier validation from model-performance claims. The canonical zero-cost evidence under `results/public/v0.4.0/` supports statements about the released verifier, attacks, valid controls, reward, and execution parity. A model leaderboard requires separately generated model trajectories under a documented evaluation protocol.

Do not treat multiple rollouts from one task as additional task diversity. Report both the number of distinct tasks and the number of rollouts per task. If a model comparison uses public development tasks, state that the tasks are inspectable and are not claimed to be contamination resistant.
