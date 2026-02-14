import unittest

from modules.financelab.schemas import FinanceLabSchemaError, validate_import_preview_input, validate_write_transaction_input
from modules.financelab.service import FinanceLabService
from memory_service.service import PostgresMemoryService
from pathlib import Path


class FinanceLabUnitTests(unittest.TestCase):
    def test_schema_validation(self):
        with self.assertRaises(FinanceLabSchemaError):
            validate_import_preview_input({})
        validate_import_preview_input({"source_doc_id": "x", "mapping": {"date": "date", "amount": "amount"}})
        with self.assertRaises(FinanceLabSchemaError):
            validate_write_transaction_input({"amount": 1})

    def test_hash_stable(self):
        repo = str(Path(__file__).resolve().parents[1])
        svc = FinanceLabService(repo, PostgresMemoryService.build())
        row = {"ts": "2026-01-01T00:00:00Z", "amount": 12.5, "merchant": "A", "note": "N"}
        h1 = svc._row_hash(row, "USD")
        h2 = svc._row_hash(row, "USD")
        self.assertEqual(h1, h2)


if __name__ == "__main__":
    unittest.main()
