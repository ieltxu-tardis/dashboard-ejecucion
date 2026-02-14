import unittest

from memory_service.policy import WritePolicyEngine


class TestWritePolicy(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = WritePolicyEngine()

    def test_allow_explicit_user_intent(self):
        d = self.policy.evaluate(
            intent_type="explicit_user_intent",
            reason="user asked",
            source="chat",
            scope="memory:write",
            confidence=0.9,
            schema_valid=False,
        )
        self.assertTrue(d.allowed)

    def test_deny_missing_reason(self):
        d = self.policy.evaluate(
            intent_type="explicit_command",
            reason="",
            source="chat",
            scope="memory:write",
            confidence=0.9,
            schema_valid=False,
        )
        self.assertFalse(d.allowed)
        self.assertEqual(d.reason, "missing_reason_source_or_scope")

    def test_deny_extraction_without_schema(self):
        d = self.policy.evaluate(
            intent_type="validated_structured_extraction",
            reason="parsed",
            source="extractor",
            scope="memory:write",
            confidence=0.95,
            schema_valid=False,
        )
        self.assertFalse(d.allowed)
        self.assertEqual(d.reason, "schema_validation_required")

    def test_deny_extraction_low_confidence(self):
        d = self.policy.evaluate(
            intent_type="validated_structured_extraction",
            reason="parsed",
            source="extractor",
            scope="memory:write",
            confidence=0.7,
            schema_valid=True,
        )
        self.assertFalse(d.allowed)
        self.assertEqual(d.reason, "confidence_too_low_for_extraction")


if __name__ == "__main__":
    unittest.main()
