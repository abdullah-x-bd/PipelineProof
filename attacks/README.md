# Adversarial cheat battery

This directory will hold versioned invalid candidate solutions used to measure observed false accepts.

The initial battery must cover:

- Constant output
- Hardcoded visible answers
- Output-shape forgery
- Reading or importing references
- Fake success metrics or stdout
- Public-test-specific conditionals
- Protected-file modification
- Trusted-metric monkeypatching

Every attack needs a label explaining why the solution is invalid, the verifier version tested, the observed reward components, and whether the exploit survived.
