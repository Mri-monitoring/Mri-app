import unittest
from Mri.caffe import TrainingCaffeEvent


class TestTrainingCaffeEvent(unittest.TestCase):
    def test_equality(self):
        event_one = TrainingCaffeEvent(500, 0.167, None)
        event_two = TrainingCaffeEvent(500.0, 0.1670, None)
        self.assertEqual(event_one, event_two)

        event_one = TrainingCaffeEvent(500, 0.167, 0.976)
        event_two = TrainingCaffeEvent(None, 0.1670, 0.976)
        self.assertNotEqual(event_one, event_two)

if __name__ == '__main__':
    unittest.main()
