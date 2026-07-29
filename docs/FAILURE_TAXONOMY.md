# Failure taxonomy

| Class | Meaning |
|---|---|
| `invalid_interface` | The repository no longer exposes the required command interface. |
| `protected_surface_violation` | A file outside `src/**` was changed, added, removed, or replaced by a symlink. |
| `public_regression` | Public tests fail. |
| `functional_failure` | Hidden outcome accuracy or partition validity fails. |
| `causal_contract_failure` | The intended information-flow or invariance contract fails. |
| `persistence_failure` | Reloaded state or repeated execution is inconsistent. |
| `accepted` | All checks pass. |

Infrastructure failures must be recorded separately from model failures. A timeout, broken image, dependency problem, or ambiguous task is not automatically a capability failure.
