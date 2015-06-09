from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
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

    def test_create_from_dict(self):
        event = TrainingEvent(500, 0.05, 0.10)
        event_dict = {'iteration': 500, 'loss': 0.05, 'accuracy': 0.10}
        self.assertEqual(event, TrainingEvent.create_from_dict(event_dict))

if __name__ == '__main__':
    unittest.main()
