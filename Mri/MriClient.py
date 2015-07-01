from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import logging
import configparser
import os
import time
import queue
import threading

from Mri.process import CaffeProcess, DummyProcess
from Mri.dispatch import MatplotlibDispatch, MriServerDispatch
from Mri.retrieve import LocalRetrieve
from Mri.utilities import verify_config


class MriClient(object):
    def __init__(self, config_file):
        """Initialize application

        Arguments
        ----------
        config_file : string
            Configuration file to load
        """
        self._retrieve = None
        self._dispatch = None

        # Verify and load configuration file
        verify_config(config_file)
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self._init_logging()
        logging.info('Started MRI client at {0}'.format(time.ctime()))
        logging.info('Read config file at {0}'.format(config_file))

    def start(self):
        """Start the Caffe thread and run forever reading events"""
        self._retrieve = self._gen_retrieve()
        if self._retrieve:
            for task in self._retrieve.retrieve_task():
                logging.info('Running task {0} (id={1})'.format(task['name'], task['id']))
                # Get dispatch based on type. Each task has it's own dispatch, but a dispatch
                # covers all the directives under a certain task.
                self._dispatch = self._gen_dispatch(task)
                for directive in task['directives']:
                    logging.info('Directive found! Type: {0}'.format(directive['type']))
                    logging.debug('Full directive: {0}'.format(directive))
                    directive_params = directive['parameters']
                    if directive['type'] == 'train':
                        self._run_train_directive(directive_params)
        else:
            logging.error('Warning, could not create retriever for this task! Skipping')

    def _run_train_directive(self, directive_params):
        """Run a directive using the JSON parameters"""
        # Non-blocking thread safe queue for incoming events
        event_queue = queue.Queue()
        # Run directive on a separate thread, non-blocking
        logging.info('Processing directive on separate thread')

        # Convert the URI to a file on the local machine
        # For local retrievers this is just the file, but for network
        # retrievers we'll download the file to a temp file
        directive_params['local_solver'] = self._retrieve.retrieve_file(directive_params['solver'])
        logging.debug('Using local solver {0}'.format(directive_params['local_solver']))

        solver_type = self.config.get('mri-client', 'solver_type').lower()
        if solver_type == 'caffe':
            process = CaffeProcess(directive_params, self.config, event_queue)
            caffe_thread = threading.Thread(target=process.train)
            caffe_thread.start()
            logging.info('Started Caffe solver backend!')
        elif solver_type == 'dummy':
            process = DummyProcess(directive_params, self.config, event_queue)
            logging.info('Dummy solver backend detected')
        else:
            logging.error('Invalid configuration file, {0} not recognized as type of solver'.format(solver_type))
            raise ValueError('Invalid configuration file')

        # Event loop to process incoming messages from Caffe
        while process.alive:
            if not event_queue.empty():
                item = event_queue.get()
                logging.debug('Processed item! Contents: {0}'.format(item))
                self._dispatch.train_event(item)
            # Hand-off CPU
            time.sleep(0.1)
        self._dispatch.train_finish()

    def _gen_dispatch(self, task):
        # Get dispatch based on type
        dispatch_type = self.config.get('mri-client', 'dispatch').lower()
        if dispatch_type == 'matplotlib-dispatch':
            folder = os.path.join(self.config.get('matplotlib-dispatch', 'save_img_folder'))
            dispatch = MatplotlibDispatch(task, folder)
            dispatch.setup_display('iteration', ['iteration', 'loss', 'accuracy'])
        elif dispatch_type == 'mri-server-dispatch':
            url = self.config.get('mri-server-dispatch', 'url')
            username = self.config.get('mri-server-dispatch', 'username')
            password = self.config.get('mri-server-dispatch', 'password')
            dispatch = MriServerDispatch(task, url, username, password)
            dispatch.setup_display('iteration', ['iteration', 'loss', 'accuracy'])
        else:
            logging.error('Invalid configuration file, please select a dispatch')
            raise Exception('Invalid configuration file, please select a dispatch')

        return dispatch

    def _gen_retrieve(self):
        """Create retrieve from config file"""
        # Retriever gets new Caffe tasks
        retrieve_type = self.config.get('mri-client', 'retrieve').lower()
        if retrieve_type == 'local-retrieve':
            return LocalRetrieve(self.config.get('local-retrieve', 'task_list'))

    def _init_logging(self):
        """Setup logger to file and console"""
        log_location = os.path.abspath(self.config.get('mri-client', 'log_location'))
        log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        root_logger = logging.getLogger()

        # Send everything to console if debug mode
        if self.config.get('mri-client', 'debug').lower() == 'true':
            root_logger.level = logging.DEBUG
            file_handler = logging.FileHandler(log_location)
            file_handler.setFormatter(log_formatter)
            root_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)
        logging.info('Log location at {0}'.format(log_location))

