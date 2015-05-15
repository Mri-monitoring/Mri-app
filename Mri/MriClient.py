import logging
import configparser
import os
import time
import queue
import threading

from Mri.caffe import CaffeWrapper
from Mri.dispatch import MatplotlibDispatch, MriServerDispatch
from Mri.retrieve import LocalRetrieve


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
        self.config = configparser.ConfigParser()
        try:
            self.config.read(config_file)
        except Exception as e:
            print('Failed to parse config file')
            raise e

        self._init_logging()
        logging.info('Started MRI client at {0}'.format(time.ctime()))
        logging.info('Read config file at {0}'.format(config_file))

    def start(self):
        """Start the Caffe thread and run forever reading events"""
        self._retrieve = self._gen_retrieve()
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
                    self._run_caffe_train(directive_params)

    def _run_caffe_train(self, train_directives):
        """Start running Caffe training using a dispatch specified in config"""
        def run_train():
            caffe = CaffeWrapper(event_queue)
            caffe_root = self.config['mri-client']['caffe_root']
            # Convert the URI to a file on the local machine
            # For local retrievers this is just the file, but for network
            # retrievers we'll download the file to a temp file
            solver_path = self._retrieve.retrieve_file(train_directives['solver'])
            logging.debug('Using local solver {0}'.format(solver_path))
            caffe.train(caffe_root, solver_path)

        # Non-blocking thread safe queue for incoming events
        event_queue = queue.Queue()
        # Run Caffe on a separate thread, non-blocking
        logging.info('Spinning up Caffe for training')
        caffe_thread = threading.Thread(target=run_train)
        caffe_thread.start()
        # Event loop to process incoming messages from Caffe
        while caffe_thread.is_alive():
            if not event_queue.empty():
                item = event_queue.get()
                logging.debug('Processed item! Contents: {0}'.format(item))
                self._dispatch.train_event(item)
            # Handoff CPU
            time.sleep(0.1)
        self._dispatch.train_finish()

    def _gen_dispatch(self, task):
        # Get dispatch based on type
        dispatch_type = self.config['mri-client']['dispatch'].lower()
        if dispatch_type == 'matplotlib-dispatch':
            folder = os.path.join(self.config['matplotlib-dispatch']['save_img_folder'])
            dispatch = MatplotlibDispatch(task, folder)
        elif dispatch_type == 'mri-server-dispatch':
            url = self.config['mri-server-dispatch']['url']
            username = self.config['mri-server-dispatch']['username']
            password = self.config['mri-server-dispatch']['password']
            dispatch = MriServerDispatch(task, url, username, password)
            dispatch.setup_display()
        else:
            logging.error('Invalid configuration file, please select a dispatch')
            raise Exception('Invalid configuration file, please select a dispatch')

        return dispatch

    def _gen_retrieve(self):
        """Create retrieve from config file"""
        # Retriever gets new Caffe tasks
        retrieve_type = self.config['mri-client']['retrieve'].lower()
        if retrieve_type == 'local-retrieve':
            return LocalRetrieve(self.config['local-retrieve']['task_list'])

    def _init_logging(self):
        """Setup logger to file and console"""
        log_location = os.path.abspath(self.config['mri-client']['log_location'])
        log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        root_logger = logging.getLogger()

        # Send everything to console if debug mode
        if self.config['mri-client']['debug'].lower() == 'true':
            root_logger.level = logging.DEBUG
            file_handler = logging.FileHandler(log_location)
            file_handler.setFormatter(log_formatter)
            root_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)
        logging.info('Log location at {0}'.format(log_location))

