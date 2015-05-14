import unittest
from Mri.caffe.helpers import parse_train_line


class TestHelpers(unittest.TestCase):
    def test_parsing(self):
        loss_line = bytes(
            'I0513 14:21:43.655602 26473 solver.cpp:189] Iteration 100, loss = 0.507584', 'UTF-8'
        )
        acc_line = bytes(
            'I0513 14:19:59.483320 26473 solver.cpp:315]     Test net output #0: accuracy = 0.789375', 'UTF-8'
        )
        no_line = bytes(
            'I0513 14:18:54.059476 26473 net.cpp:169] accuracy does not need backward computation.', 'UTF-8'
        )
        parsed = {'iteration': 100, 'loss': 0.507584}
        self.assertEqual(parse_train_line(loss_line), parsed)
        parsed = {'iteration': 200, 'loss': 0.57584}
        self.assertNotEqual(parse_train_line(loss_line), parsed)
        parsed = {'accuracy': 0.789375}
        self.assertEqual(parse_train_line(acc_line), parsed)

        self.assertEqual(parse_train_line(no_line), {})

if __name__ == '__main__':
    unittest.main()
