import unittest

from memory_service.jobs import compute_backoff_seconds, should_retry


class TestJobsUnit(unittest.TestCase):
    def test_backoff(self):
        self.assertEqual(compute_backoff_seconds(1, 2), 2)
        self.assertEqual(compute_backoff_seconds(2, 2), 4)
        self.assertEqual(compute_backoff_seconds(3, 2), 8)

    def test_should_retry(self):
        self.assertTrue(should_retry(0, 3))
        self.assertTrue(should_retry(2, 3))
        self.assertFalse(should_retry(3, 3))


if __name__ == "__main__":
    unittest.main()
