from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import bytes
from future import standard_library
standard_library.install_aliases()
import unittest
import tempfile

from Mri.utilities import verify_config

good_config = '''
; ---=== Dispatch Settings ===---
; Dispatches events to be plotted locally in Matplotlib
[matplotlib-dispatch]
save_img_folder = {0}

; Dispatches events to an mri-server
[mri-server-dispatch]
url = http://httpbin.org
username = test
password = test

; ---=== Retrieve Settings ===---
; Retrieve events from a local folder
[local-retrieve]
task_list = /bin/ls

; ---=== Client Settings ===---
[mri-client]
log_location = /tmp/LogTmpTest.txt
debug = True
caffe_root = /bin
caffe_bin = true
solver_type = Caffe

; Dispatch and Retrieve modules to use
dispatch = mri-server-dispatch
retrieve = local-retrieve
'''.format(tempfile.tempdir)

bad_config = '''
; ---=== Dispatch Settings ===---
; Dispatches events to be plotted locally in Matplotlib
[matplotlib-dispatch]
save_img_folder = {0}

; Dispatches events to an mri-server
[mri-server-dispatch]
url = http://httpbin.org
username = test
password = test

; ---=== Retrieve Settings ===---
; Retrieve events from a local folder
[local-retrieve]
task_list = /path/to/local_235h98ghw.txt

; ---=== Client Settings ===---
[mri-client]
log_location = /tmp/LOGtmpTEST.txt
debug = True
caffe_root = /bin
caffe_bin = true
solver_type = Caffe

; Dispatch and Retrieve modules to use
dispatch = mri-server-dispatch
retrieve = local-retrieve
'''.format(tempfile.tempdir)


class TestVerifyConfig(unittest.TestCase):
    def test_good_config(self):
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(bytes(good_config, 'UTF-8'))
        temp.close()
        verify_config(temp.name)

    def test_bad_config(self):
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(bytes(bad_config, 'UTF-8'))
        temp.close()
        with self.assertRaises(ValueError):
            verify_config(temp.name)

if __name__ == '__main__':
    unittest.main()