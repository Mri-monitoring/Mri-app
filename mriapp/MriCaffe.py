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
import tempfile
import uuid
import json

from mri.dispatch import MatplotlibDispatch, MriServerDispatch

from mriapp.retrieve import LocalRetrieve
from mriapp.process import CaffeProcess, DummyProcess
from mriapp.utilities import verify_config


class MriCaffe(object):
    def __init__(self, config_file, solver_override):
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

        # Start logging
        self._init_logging()
        logging.info('Started MRI client at {0}'.format(time.ctime()))
        logging.info('Read config file at {0}'.format(config_file))

        # Check the override solver prototext
        if solver_override:
            logging.info('Override prototext detected, using file {} instead of task list'.format(solver_override))
            if not os.path.isfile(solver_override):
                raise ValueError('Cannot find solver file for override')
            self.solver_override = solver_override
        else:
            self.solver_override = None

    def start(self):
        """Start the Caffe thread and run forever reading events"""
        self._retrieve = self._gen_retrieve()
        if self._retrieve:
            for task in self._retrieve.retrieve_task():
                logging.info('Running task {0} (id={1})'.format(task['title'], task['id']))
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

    def _get_config(self, *args):
        """Get a config variable or return None instead of throwing an exception"""
        config = self.config
        value = None
        try:
            value = config.get(*args)
        except configparser.NoOptionError:
            pass
        return value

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

        solver_type = self._get_config('mri-client', 'solver_type').lower()
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
            time.sleep(0.05)
        self._dispatch.train_finish()

    def _gen_dispatch(self, task):
        # Get dispatch based on type
        dispatch_type = self._get_config('mri-client', 'dispatch').lower()
        if dispatch_type == 'matplotlib-dispatch':
            folder = os.path.join(self._get_config('matplotlib-dispatch', 'save_img_folder'))
            dispatch = MatplotlibDispatch(task, folder)
            windows = self._get_config('matplotlib-dispatch', 'show_windows')
            if windows:
                show_windows = windows.lower() == 'true'
            else:
                show_windows = False

            dispatch.setup_display('iteration', ['iteration', 'loss', 'accuracy'], show_windows=show_windows)
        elif dispatch_type == 'mri-server-dispatch':
            url = self._get_config('mri-server-dispatch', 'url')
            username = self._get_config('mri-server-dispatch', 'username')
            password = self._get_config('mri-server-dispatch', 'password')
            dispatch = MriServerDispatch(task, url, username, password)
            dispatch.setup_display('iteration', ['iteration', 'loss', 'accuracy'])
        else:
            logging.error('Invalid configuration file, please select a dispatch')
            raise Exception('Invalid configuration file, please select a dispatch')

        return dispatch

    def _gen_false_local_retrieve(self):
        """Create a local retrieve for a single solver in a temp directory"""
        # Create the temp dir
        temp_dir = tempfile.mkdtemp()
        # Create the temp task
        name = os.path.split(self.solver_override)[1]
        id = str(uuid.uuid1())
        logging.debug('Creating a task for {} named {}, id {}'.format(self.solver_override, name, id))

        temp_task = os.path.join(temp_dir, 'task.json')
        with open(temp_task, 'w') as f:
            train_directive = [{'type': 'train', 'parameters': {'solver': self.solver_override}}]
            task_file = {'directives': train_directive, 'title': name, 'id': id}
            json.dump(task_file, f)
        # Create the temp list containing one task
        temp_task_list = tempfile.NamedTemporaryFile()
        print(temp_task, file=temp_task_list)
        logging.debug('Created task list with single task at {}'.format(temp_task_list.name))
        return LocalRetrieve(temp_task_list.name)

    def _gen_retrieve(self):
        """Create retrieve from config file"""
        # Retriever gets new Caffe tasks
        # If we don't want to override via solver get the specified retriever
        if not self.solver_override:
            logging.debug("Generating retriever specified in config file")
            retrieve_type = self._get_config('mri-client', 'retrieve').lower()
            if retrieve_type == 'local-retrieve':
                return LocalRetrieve(self._get_config('local-retrieve', 'task_list'))
        # Otherwise we'll override by creating a false task list and false task (local)
        else:
            logging.debug("Overriding retriever via command line")
            return self._gen_false_local_retrieve()

    def _init_logging(self):
        """Setup logger to file and console"""
        log_location = os.path.abspath(self._get_config('mri-client', 'log_location'))
        log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        root_logger = logging.getLogger()

        # Send everything to console if debug mode
        log_mode = self._get_config('mri-client', 'log_level').lower()
        if log_mode == 'debug' or log_mode == 'info':
            if log_mode == 'debug':
                root_logger.level = logging.DEBUG
            else:
                root_logger.level = logging.INFO
            file_handler = logging.FileHandler(log_location)
            file_handler.setFormatter(log_formatter)
            root_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)
        logging.info('Log location at {0}'.format(log_location))

