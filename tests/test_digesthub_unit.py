import unittest

from modules.digesthub.schemas import DigestHubSchemaError, validate_send_now, validate_subscribe_daily


class DigestHubUnitTests(unittest.TestCase):
    def test_schemas(self):
        with self.assertRaises(DigestHubSchemaError):
            validate_subscribe_daily({})
        validate_subscribe_daily({"actor_id": "123"})
        with self.assertRaises(DigestHubSchemaError):
            validate_send_now({"actor_id": "123"})


if __name__ == "__main__":
    unittest.main()
