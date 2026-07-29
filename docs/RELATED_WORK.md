# Related work

SWE-bench evaluates repository repair from real GitHub issues and primarily scores fail-to-pass tests. PipelineProof uses smaller original repositories and targets failures that can retain passing public tests and plausible outputs.

MLE-bench evaluates end-to-end ML engineering through Kaggle competitions. ML-Dev-Bench and ML-Bench cover practical ML development and repository-level agent work. PipelineProof narrows the target to causal integrity contracts and verifier soundness.

TrainCheck detects silent deep-learning training errors through inferred invariants. PipelineProof shares the emphasis on silent failure but asks a coding agent to repair the repository and accepts multiple implementations through behavioural verification.

Work on leakage in ML pipelines motivates the provenance and evaluation families. PipelineProof turns those failure mechanisms into executable repair tasks.

PipelineProof does not claim to be the first ML debugging benchmark. Its contribution is the combination of original repair tasks, hidden interventions, alternative-correct controls, a versioned attack battery, and an RL-compatible graded reward.

## References

- Jimenez et al. SWE-bench. ICLR 2024. arXiv:2310.06770.
- Chan et al. MLE-bench. arXiv:2410.07095.
- Padigela, Shah, and Juyal. ML-Dev-Bench. arXiv:2502.00964.
- Tang et al. ML-Bench. arXiv:2311.09835.
- Jiang et al. Training with Confidence: Catching Silent Errors in Deep Learning Training with Automated Proactive Checks. arXiv:2506.14813.
- Sasse et al. On Leakage in Machine Learning Pipelines. arXiv:2311.04179.
