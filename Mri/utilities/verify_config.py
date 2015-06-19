from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import configparser
import os
import requests
import subprocess


def verify_config(filename):
    """Verify a configuration file prior to loading the full program. This will hopefully prevent
    unfortunate config errors where some events have already occurred, such as accessing the server

    Arguments
    ----------
    filename : string
        Config file to test
    """
    # Open the config file
    config = configparser.ConfigParser()
    config.read(filename)

    # Check which dispatch and retrieve modules to use
    dispatch = config.get('mri-client', 'dispatch')
    retrieve = config.get('mri-client', 'retrieve')

    # Verify Dispatchers
    if dispatch == 'mri-server-dispatch':
        # Try to access the server
        auth = (config.get('mri-server-dispatch', 'username'), config.get('mri-server-dispatch', 'password'))
        url = config.get('mri-server-dispatch', 'url')
        result = requests.request(method='GET', url=url, auth=auth)
        if result.status_code is not 200:
            raise RuntimeError(
                'Failed to access the server specified in config.'
                'Please verify the config file is correct and the server'
                'is accessible with the given credentials.'
            )
    elif dispatch == 'matplotlib-dispatch':
        save = config.get('matplotlib-dispatch', 'save_img_folder')
        if not os.path.isdir(save):
            raise ValueError('Image save folder specified in config file is not valid')
    else:
        raise ValueError('Invalid dispatch found in config file')

    # Verify retrievers
    if retrieve == 'local-retrieve':
        # Check that the task list is a real file
        task_list = config.get('local-retrieve', 'task_list')
        if not os.path.isfile(task_list):
            raise ValueError('Task list specified in config file not found')
    else:
        raise ValueError('Invalid retrieve found in config file')

    # Verify log
    if not os.path.isfile(config.get('mri-client', 'log_location')):
        raise ValueError('Log file specified in config file appears invalid')
    # Verify Caffe
    caffe_root = config.get('mri-client', 'caffe_root')
    if not os.path.isdir(caffe_root):
        raise ValueError('Caffe root folder specified in config appears invalid')
    # Verify Caffe path
    caffe = config.get('mri-client', 'caffe_bin')
    caffe_path = os.path.abspath(os.path.join(caffe_root, caffe))
    ret_val = subprocess.call(caffe_path)
    if ret_val is not 0:
        raise ValueError('An error occurred when trying to access Caffe, please check your config file')

    # Verify solver type
    solver = config.get('mri-client', 'solver_type')
    if solver != 'Caffe':
        raise ValueError('Solver type specified in config unrecognized')
