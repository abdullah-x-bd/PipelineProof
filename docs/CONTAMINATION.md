# Provenance and contamination

All task code, prompts, verifiers, controls, and attacks were written for PipelineProof.

No client work or data-vendor material was used.

The data are generated locally from private task specifications. Public task manifests exclude coefficients, intercepts, and verifier seeds.

The evaluation bundle is kept outside the public repository. It uses:

- Different feature schemas
- Different ground-truth functions
- Different seeds
- A different repository structure
- Separate quality seeds

Each private file is covered by a SHA-256 manifest. The public release also includes a file-hash manifest.

This establishes provenance and exact-instance freshness. It does not prove that no model has seen the general bug classes.
