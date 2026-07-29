from __future__ import annotations


def classify(checks: dict[str, bool]) -> str:
    if not checks.get("interface", False):
        return "invalid_interface"
    if not checks.get("protected", False):
        return "protected_surface_violation"
    if not checks.get("public_tests", False):
        return "public_regression"
    if not checks.get("functional", False):
        return "functional_failure"
    if not checks.get("causal", False):
        return "causal_contract_failure"
    if not checks.get("persistence", False):
        return "persistence_failure"
    return "accepted"
