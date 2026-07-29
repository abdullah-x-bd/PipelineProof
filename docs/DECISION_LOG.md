# Decision log

This file records material decisions, reversals, and discovered mistakes. Entries should describe the evidence that changed the design rather than retroactively presenting every choice as obvious.

## 2026-07-29

### Narrow the capability target

**Decision:** Define PipelineProof around ML pipeline integrity contracts rather than a broad collection of silent ML bugs.

**Reason:** A collection mixing data leakage, domain equations, hyperparameters, units, serialization, and general modelling errors would be difficult to interpret as one capability. Training provenance, evaluation validity, and train-serving equivalence provide a coherent causal frame.

### Start with feature-schema mismatch

**Decision:** Implement feature-schema mismatch before leakage tasks.

**Reason:** It supports cheap deterministic execution, multiple valid repairs, and patch-independent metamorphic verification. This lets the project test the complete environment architecture before adding harder provenance instrumentation.

### Do not claim long-horizon status

**Decision:** Treat the first release as repository-level, single-task-per-rollout work.

**Reason:** Difficulty and repository breadth alone do not establish the required persistent state, heterogeneous tool use, causal step depth, and failure recovery.

### Keep private assets outside the public repository

**Decision:** Commit schemas, public tasks, and reproducibility code while excluding oracle material, private seeds, and final evaluation assets.

**Reason:** A hidden path inside an agent-visible repository is not a meaningful isolation boundary.
