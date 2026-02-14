from dataclasses import dataclass
from typing import Optional


ALLOWED_INTENT_TYPES = {
    "explicit_user_intent",
    "explicit_command",
    "validated_structured_extraction",
}


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str


class WritePolicyEngine:
    """Memory write policy guard.

    Allowed only when:
    - intent_type in allowed set
    - reason/source/scope present
    - confidence provided
    - validated_structured_extraction requires confidence >= 0.85 and schema_valid=True
    """

    def evaluate(
        self,
        *,
        intent_type: str,
        reason: str,
        source: str,
        scope: str,
        confidence: Optional[float],
        schema_valid: bool = False,
    ) -> PolicyDecision:
        if intent_type not in ALLOWED_INTENT_TYPES:
            return PolicyDecision(False, "intent_type_not_allowed")

        if not reason or not source or not scope:
            return PolicyDecision(False, "missing_reason_source_or_scope")

        if confidence is None:
            return PolicyDecision(False, "missing_confidence")

        if confidence < 0 or confidence > 1:
            return PolicyDecision(False, "confidence_out_of_range")

        if intent_type == "validated_structured_extraction":
            if not schema_valid:
                return PolicyDecision(False, "schema_validation_required")
            if confidence < 0.85:
                return PolicyDecision(False, "confidence_too_low_for_extraction")

        return PolicyDecision(True, "allowed")
