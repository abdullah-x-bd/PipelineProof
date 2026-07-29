# Trial reasoning

## Bio and role

I build and lead technical AI governance work. I founded Project AWARE, which works on institutional AI safety, and Zephara AI, where I have led applied AI product development. I have worked as an AI engineer on production document systems and teach digital transformation as visiting faculty. My strongest contribution is combining technical implementation with evaluation design, threat modelling, and quality review.

I am suited to both environment building and build leadership. I can implement Python and ML evaluation systems directly, define what a reward does and does not establish, review task validity, and coordinate researchers. My current gaps are production-scale untrusted-code orchestration, large multi-provider model sweeps, and operating hardened sandbox infrastructure at lab volume.

## Targeted weakness

PipelineProof targets coding agents that make a repository appear repaired while leaving an ML pipeline scientifically or operationally invalid. The six tasks cover provenance, evaluation, and train-serving equivalence. Each broken repository runs, passes public tests, and emits plausible output.

This is narrower than general repository repair and ML engineering benchmarks. The relevant capability is recognising and restoring a hidden behavioural contract when visible success signals are insufficient.

## Reward design

The verifier scores outcomes. It accepts different implementations and does not compare patches. The strongest reward component is the family-specific causal intervention. Functional correctness gates causal and persistence credit so a constant predictor cannot earn reward merely by being invariant.

An independent quality suite uses different seeds and stronger interventions. It is not used to calculate reward.

## Contamination

The task repositories and data are original. Public manifests omit oracle coefficients and verifier seeds. Evaluation tasks, specifications, quality seeds, gold repairs, and alternatives are held in a separate bundle. No previous client material was used.

## Attempts to break the verifier

The first battery covers constant output, hardcoded examples, output-shape forgery, fake stdout, public-test conditionals, internal imports, metric monkeypatching, and protected-file edits. The current local receipt observed zero false accepts in 32 trials and zero false rejects in 12 valid-solution trials. The Wilson intervals remain nonzero because the sample is finite and structurally correlated.

## One design mistake

The first feature-schema verifier serialized hidden rows with sorted JSON keys. Sorting erased the key-order intervention, allowing the broken implementation to appear invariant. The request writer now preserves insertion order, and the independent suite tests multiple rotations.

A second error was treating causal invariance as independently rewardable. Constant outputs are invariant but do not solve the task. Causal and persistence rewards are now gated on hidden functional correctness.

## Evidence

- Six development tasks
- Six held-back evaluation tasks
- Eighteen public valid repair controls
- Eight attack classes
- Zero observed false accepts in 32 trials
- Zero observed false rejects in 12 trials
- All 18 valid family controls accepted
- All six broken family controls rejected
- Strictly monotonic five-level reward ladder
- No high-variance control cells across four deterministic seeds

## Limits

The committed evidence uses local process isolation. Docker configuration is implemented but was not executed on the build host. The tasks use small deterministic models. A frontier-model panel, scaffold comparison, and model-generated best-of-N sweep remain unrun. The labelled-candidate search is a verifier sanity check, not a replacement for those experiments.

## Comments on the checklist

A false-accept rate is conditional on a named verifier version and attack distribution. It should not be presented as a permanent property.

Generated instances from one mutation template are correlated. Confidence intervals should cluster by structural template or defect family.

Hidden-test secrecy and runtime isolation are separate claims. A hidden file can still leak through a mount or import path.

A coding-agent leaderboard measures model, scaffold, provider route, and resource policy together unless those effects are varied or disclosed.
