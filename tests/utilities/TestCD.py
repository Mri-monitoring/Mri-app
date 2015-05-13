import unittest
import os
import tempfile
from Mri.utilities import cd


class TestCD(unittest.TestCase):
    def test_cd(self):
        tempdir = tempfile.tempdir
        with cd(tempdir):
            cwd = os.getcwd()
            self.assertEqual(cwd, '/tmp')


if __name__ == '__main__':
    unittest.main()
