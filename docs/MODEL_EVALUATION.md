# Model evaluation

The environment does not call model providers directly. A harness writes one JSON object per rollout to a JSONL file.

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
