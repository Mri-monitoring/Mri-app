import unittest
from Mri.event import TrainingEvent


class TestTrainingCaffeEvent(unittest.TestCase):
    def test_equality(self):
        event_one = TrainingEvent(500, 0.167, None)
        event_two = TrainingEvent(500.0, 0.1670, None)
        self.assertEqual(event_one, event_two)

        event_one = TrainingEvent(500, 0.167, 0.976)
        event_two = TrainingEvent(400, 0.1670, 0.976)
        self.assertNotEqual(event_one, event_two)

        with self.assertRaises(ValueError):
            _ = TrainingEvent(None, 1.0, 1.0)

if __name__ == '__main__':
    unittest.main()
