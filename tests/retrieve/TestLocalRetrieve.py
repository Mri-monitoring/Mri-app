from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import bytes
from future import standard_library
standard_library.install_aliases()
import os
import unittest
import tempfile

from Mri.retrieve import LocalRetrieve


class TestLocalRetrieve(unittest.TestCase):
    _test_task = """{
        "directives": [{
            "type": "train",
            "parameters": {
            "model": "/home/user/folder/002/model.prototxt",
            "solver": "/home/user/folder/002/solver.prototxt"
            }
        }],
        "name": "Mri Test",
        "id": "554d0b8888fce10300bf0bdf"
    }"""

    def setUp(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(bytes(self._test_task, 'UTF-8'))
        f.close()
        self.taskfile = f.name

        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(bytes(self.taskfile, 'UTF-8'))
        f.close()
        self.listfile = f.name

    def tearDown(self):
        os.remove(self.taskfile)
        os.remove(self.listfile)

    def test_local_retrieve_file(self):
        self.instance = LocalRetrieve(self.listfile)
        test_str = "/home/testuser/folder/folder/model.prototxt"
        ident = self.instance.retrieve_file(test_str)
        self.assertEqual(ident, test_str)

    def test_local_retrieve_task(self):
        self.instance = LocalRetrieve(self.listfile)
        for task in self.instance.retrieve_task():
            self.assertEqual(task['id'], '554d0b8888fce10300bf0bdf')
            self.assertEqual(len(task['directives']), 1)


if __name__ == '__main__':
    unittest.main()
