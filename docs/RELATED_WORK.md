# Related work

PipelineProof sits at the intersection of repository-level software-agent evaluation, machine-learning engineering benchmarks, silent-error detection, and leakage-aware ML evaluation. Its intended contribution is narrower than any claim to be the first ML debugging benchmark.

## Repository-level software engineering benchmarks

### SWE-bench

SWE-bench asks language models to resolve real GitHub issues in existing Python repositories and grades resulting patches against repository tests. Its central contribution is realistic repository-level issue resolution rather than isolated code generation.

PipelineProof adopts the same broad principle that agent capability should be evaluated through **execution in a repository**, but its task construction is different. PipelineProof uses compact original ML repositories whose visible tests are deliberately insufficient: a candidate can execute and satisfy the public surface while still violating a held-back ML integrity contract.

Reference: Jimenez et al., *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?*, ICLR 2024, arXiv:2310.06770.

## Machine-learning engineering agent benchmarks

### MLE-bench

MLE-bench evaluates end-to-end ML engineering capability through 75 Kaggle competitions. Agents must work with data, train models, iterate on experiments, and achieve externally meaningful leaderboard performance.

PipelineProof is intentionally much smaller and more diagnostic. It does not evaluate whether an agent can win an ML competition. It asks whether an agent can repair a specific silent pipeline-integrity defect without gaming a held-back executable verifier.

Reference: Chan et al., *MLE-bench: Evaluating Machine Learning Agents on Machine Learning Engineering*, arXiv:2410.07095.

### MLAgentBench

MLAgentBench evaluates language agents on iterative ML experimentation across 13 tasks, including reading and writing files, executing experiments, interpreting results, and improving models.

PipelineProof differs in the unit of success. The target is not open-ended experimental improvement but repository repair under explicit hidden integrity contracts. This makes verifier soundness, alternative-correct repairs, and adversarial candidate construction first-class benchmark objects.

Reference: Huang et al., *MLAgentBench: Evaluating Language Agents on Machine Learning Experimentation*, arXiv:2310.03302.

### ML-Bench

ML-Bench evaluates LLMs and agents on repository-level ML code across real open-source libraries, including an autonomous-agent setting in a Linux execution environment.

PipelineProof shares the repository-execution setting but narrows the failure distribution to silent ML validity defects. Rather than asking whether generated code completes a requested repository-level task, PipelineProof tests whether an executable hidden intervention can distinguish genuine validity repair from visible-test success.

Reference: Tang et al., *ML-Bench: Evaluating Large Language Models and Agents for Machine Learning Tasks on Repository-Level Code*, arXiv:2311.09835.

### ML-Dev-Bench

ML-Dev-Bench targets applied ML development workflows such as dataset handling, training, model improvement, debugging, and API integration.

PipelineProof should therefore not be described as the first benchmark for practical ML development agents. Its narrower contribution is a benchmark where **silent integrity failures, held-back behavioural verification, attack validation, and multiple legitimate repair implementations** are jointly part of the artifact.

Reference: Padigela, Shah, and Juyal, *ML-Dev-Bench: Comparative Analysis of AI Agents on ML Development Workflows*, ICLR 2025 workshop submission, OpenReview: Ulwyv3mrQ2.

### MLGym

MLGym provides a Gym-style framework and benchmark for AI research agents across open-ended ML research tasks. It is explicitly intended to support evaluation and reinforcement-learning research over agents that generate ideas, modify code, run experiments, and analyze outcomes.

PipelineProof is also compatible with RL-style use, but the environment is deliberately constrained enough that reward semantics and verifier attacks can be audited exhaustively. The benchmark is therefore more diagnostic than open-ended research-agent environments.

Reference: Nathani et al., *MLGym: A New Framework and Benchmark for Advancing AI Research Agents*, arXiv:2502.14499.

## Silent-error detection in machine learning

### TrainCheck

TrainCheck proactively detects silent deep-learning training errors by inferring and checking training invariants. Its evaluation reproduces real silent training errors and demonstrates that many can be detected early without waiting for visible crashes.

PipelineProof shares the concern that **non-crashing ML failures can be more dangerous than ordinary exceptions**. The research object differs: TrainCheck is primarily a detection/debugging system for training errors, while PipelineProof presents repair tasks to an agent and evaluates candidate source modifications through held-back behavioural contracts.

Reference: Jiang et al., *Training with Confidence: Catching Silent Errors in Deep Learning Training with Automated Proactive Checks*, arXiv:2506.14813.

### Silent bugs in DL frameworks

Empirical work on Keras and TensorFlow has documented reproducible silent bugs that produce incorrect behaviour without explicit error signals. This literature supports the broader motivation for treating silent correctness failures as an evaluation target rather than assuming successful execution implies correctness.

Reference: Tambon et al., *Silent Bugs in Deep Learning Frameworks: An Empirical Study of Keras and TensorFlow*, arXiv:2112.13314.

## Leakage in machine-learning pipelines

Sasse et al. survey leakage mechanisms that can create overoptimistic evaluation and poor generalization. PipelineProof's preprocessing/evaluation leakage, group leakage, wrong-split evaluation, and target-derived feature families operationalize several related failure principles as executable repository-repair tasks.

PipelineProof does not claim that its six families exhaust leakage taxonomy. The benchmark uses compact representative mechanisms that can be independently generated and verified.

Reference: Sasse et al., *On Leakage in Machine Learning Pipelines*, arXiv:2311.04179.

## Benchmark validity, contamination, and verifier gaming

Repository-agent benchmarks increasingly face questions about memorization, contamination, benchmark saturation, and whether public tests measure the intended capability. PipelineProof addresses only one part of this broader problem: it makes the **public/held-back distinction and verifier attack surface explicit**.

The public development tasks remain inspectable and may eventually become training data. PipelineProof therefore does not claim contamination resistance from its public split. Instead, the design supports separately distributed private specifications and seeds for consequential model comparisons.

The adversarial battery is aimed at **verifier validity**, not at proving malicious-agent security. In v0.4, rejected malformed attack fixtures are excluded from the false-accept denominator, repeated seeds are separated from structural attack diversity, and otherwise-correct protected edits are used to isolate the benchmark-integrity detector.

## Positioning summary

PipelineProof is best described as:

> An execution-based benchmark and RL environment for repairing silent ML pipeline integrity failures, with held-back behavioural contracts, multiple valid repair implementations, a versioned adversarial verifier battery, and reproducible verifier-soundness evidence.

It is **not** best described as:

- the first ML debugging benchmark;
- a replacement for SWE-bench;
- a replacement for MLE-bench or MLAgentBench;
- a general hostile-code sandbox;
- a benchmark that already establishes frontier-model capability.

## Comparison dimensions

| Work | Repository execution | ML-specific | Open-ended ML work | Silent integrity central | Held-back behavioural verification | Explicit adversarial verifier battery | Multiple valid repair controls |
|---|---:|---:|---:|---:|---:|---:|---:|
| SWE-bench | Yes | No | No | No | Test-based | No | Not a central artifact |
| MLE-bench | Yes | Yes | Yes | No | Competition scoring | No | No |
| MLAgentBench | Yes | Yes | Yes | No | Task-specific outcomes | No | No |
| ML-Bench | Yes | Yes | Partly | No | Executable task success | No | No |
| ML-Dev-Bench | Yes | Yes | Yes | No | Task/workflow success | No | No |
| TrainCheck | Training execution | Yes | No | Yes | Invariant checks | Not an agent-repair benchmark | No |
| PipelineProof | **Yes** | **Yes** | No | **Yes** | **Yes** | **Yes** | **Yes** |

The table is conceptual rather than a claim of exhaustive feature coverage across every release of each benchmark. Readers should consult the cited primary sources for their complete protocols.

## Primary references

- Carlos E. Jimenez et al. *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* arXiv:2310.06770.
- Jun Shern Chan et al. *MLE-bench: Evaluating Machine Learning Agents on Machine Learning Engineering.* arXiv:2410.07095.
- Qian Huang et al. *MLAgentBench: Evaluating Language Agents on Machine Learning Experimentation.* arXiv:2310.03302.
- Xiangru Tang et al. *ML-Bench: Evaluating Large Language Models and Agents for Machine Learning Tasks on Repository-Level Code.* arXiv:2311.09835.
- Harshith Padigela, Chintan Shah, and Dinkar Juyal. *ML-Dev-Bench: Comparative Analysis of AI Agents on ML Development Workflows.* OpenReview Ulwyv3mrQ2.
- Deepak Nathani et al. *MLGym: A New Framework and Benchmark for Advancing AI Research Agents.* arXiv:2502.14499.
- Yuxuan Jiang et al. *Training with Confidence: Catching Silent Errors in Deep Learning Training with Automated Proactive Checks.* arXiv:2506.14813.
- Florian Tambon et al. *Silent Bugs in Deep Learning Frameworks: An Empirical Study of Keras and TensorFlow.* arXiv:2112.13314.
- Leonard Sasse et al. *On Leakage in Machine Learning Pipelines.* arXiv:2311.04179.
