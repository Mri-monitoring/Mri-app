import logging
import configparser
import os
import time
import queue
import threading

from Mri.caffe import CaffeWrapper
from Mri.dispatch import MatplotlibDispatch


class MriClient(object):
    def __init__(self, config_file):
        """Initialize application

        Arguments
        ----------
        config_file : string
            Configuration file to load
        """
        self._running = False
        self._event_queue = None
        self._caffe_thread = None
        self.config = configparser.ConfigParser()
        try:
            self.config.read(config_file)
        except Exception as e:
            logging.error('Failed to parse config file')
            raise e

        log_location = os.path.abspath(self.config['mri-client']['log_location'])
        if self.config['mri-client']['debug'].lower() == 'true':
            logging.basicConfig(filename=log_location, level=logging.DEBUG)
        else:
            logging.basicConfig(filename=log_location)

        logging.info('Started MRI client at {0}'.format(time.ctime()))
        logging.info('Read config file at {0}'.format(config_file))
        logging.info('Log location at {0}'.format(log_location))

    def start(self):
        """Start the Caffe thread and run forever reading events"""
        self._running = True
        # Non-blocking thread safe queue for incoming events
        self._event_queue = queue.Queue()
        # Run Caffe on a separate thread, non-blocking
        self._caffe_thread = threading.Thread(target=self._run_caffe_train)
        self._caffe_thread.start()
        # Event loop to process incoming messages from Caffe
        while self._running:
            if not self._event_queue.empty():
                item = self._event_queue.get()
            # Handoff CPU
            time.sleep(0.1)
        self._cleanup()

    def stop(self):
        """Stop all running processes"""
        self._cleanup()

    def _run_caffe_train(self):
        """Start running Caffe training using a dispatch specified in config"""
        dispatch_type = self.config['mri-client']['dispatch'].lower()
        if dispatch_type == 'matplotlib':
            dispatch = MatplotlibDispatch()
        caffe = CaffeWrapper(dispatch)

        caffe_root = self.config['mri-client']['caffe_root']
        solver_path = self.config['mri-client']['solver']
        caffe.solve(caffe_root, solver_path)

    def _cleanup(self):
        self._running = False
        self._event_queue = None
        if self._caffe_thread:
            self._caffe_thread.stop()
        self._caffe_thread = None
