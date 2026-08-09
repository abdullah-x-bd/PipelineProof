## Change

Describe the problem and the smallest coherent change that addresses it.

## Benchmark impact

- [ ] No benchmark semantics change
- [ ] Task semantics change
- [ ] Verifier change
- [ ] Attack-battery change
- [ ] Valid-control change
- [ ] Reward change
- [ ] Evidence-schema change
- [ ] Model-reporting change

If benchmark semantics change, describe the affected behavioural invariant and why the new design is preferable.

## Validation

- [ ] `ruff check .`
- [ ] `pytest`
- [ ] Relevant slow tests
- [ ] Docker validation when execution semantics change
- [ ] Legitimate-repair controls checked when verifier semantics change
- [ ] Adversarial controls checked when verifier semantics change
- [ ] Canonical evidence regenerated when released measurements change

## Research integrity

- [ ] Repeated seeds are not presented as structural task diversity
- [ ] Malformed attacks are not counted as soundness evidence
- [ ] Synthetic model fixtures are not presented as empirical results
- [ ] No private evaluation assets or credentials are included
- [ ] Claim-boundary documentation was updated if needed
