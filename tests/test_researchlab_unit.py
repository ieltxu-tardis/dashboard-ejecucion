import unittest

from modules.researchlab.schemas import (
    ResearchLabSchemaError,
    validate_create_collection_input,
    validate_search_input,
)


class ResearchLabUnitTests(unittest.TestCase):
    def test_schema_basics(self):
        with self.assertRaises(ResearchLabSchemaError):
            validate_create_collection_input({})
        validate_create_collection_input({"name": "alpha"})
        with self.assertRaises(ResearchLabSchemaError):
            validate_search_input({"query_text": "x", "top_k": 0})


if __name__ == "__main__":
    unittest.main()
