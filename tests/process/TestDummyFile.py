from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import unittest

from mriapp.process import DummyProcess


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