import unittest

from modules.timelab.schemas import TimeLabSchemaError, validate_capture_task_input, validate_update_task_input


class TimeLabUnitTests(unittest.TestCase):
    def test_capture_schema(self):
        with self.assertRaises(TimeLabSchemaError):
            validate_capture_task_input({})
        validate_capture_task_input({"title": "Do thing"})

    def test_update_schema(self):
        with self.assertRaises(TimeLabSchemaError):
            validate_update_task_input({"title": "x"})
        validate_update_task_input({"task_id": "abc"})


if __name__ == "__main__":
    unittest.main()
