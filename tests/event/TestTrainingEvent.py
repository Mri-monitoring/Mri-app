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
        event_one = TrainingEvent({'iteration': 500, 'loss': 0.167, 'accuracy': None}, 'iteration')
        event_two = TrainingEvent({'iteration': 500, 'loss': 0.1670, 'accuracy': None}, 'iteration')
        self.assertEqual(event_one, event_two)

        event_one = TrainingEvent({'iteration': 500, 'loss': 0.167, 'accuracy': 0.976}, 'iteration')
        event_two = TrainingEvent({'iteration': 400, 'loss': 0.1670, 'accuracy': 0.976}, 'iteration')
        self.assertNotEqual(event_one, event_two)

        with self.assertRaises(ValueError):
            _ = TrainingEvent({'loss': 0.1670, 'accuracy': 0.976}, 'iteration')

if __name__ == '__main__':
    unittest.main()
