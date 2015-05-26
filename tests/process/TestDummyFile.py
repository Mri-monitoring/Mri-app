import unittest

from Mri.process import DummyProcess


class TestDummyFile(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dummy_file(self):
        count = 0
        process = DummyProcess(None, None, None)
        while process.alive:
            count += 1
        self.assertEqual(count, 100)

if __name__ == '__main__':
    unittest.main()