from Mri.utilities import cd
from .helpers import parse_train_line
from .TrainingCaffeEvent import TrainingCaffeEvent
import subprocess
import logging


class CaffeWrapper(object):
    """Parse and send output from Caffe to Queue

    Parameters
    ----------
    action_handler : Queue
        Queue that accepts Caffe actions
    """

    def __init__(self, action_handler):
        self.action_handler = action_handler
        self.curiter = None
        self.curloss = None
        self.curacc = None

    def train(self, caffe_root, solver, caffe_path='./build/tools/caffe'):
        """Run Caffe training given the required models

        Parameters
        ----------
        caffe_root : string
            Location of the root Caffe folder

        solver: string
            Location of the solver file for this Caffe run
        """
        def _consolidate_training(train_event):
            """Combine traning event with known data"""
            if train_event:
                if train_event.accuracy:
                    self.curacc = train_event.accuracy
                if train_event.iteration:
                    self.curiter = train_event.iteration
                if train_event.loss:
                    self.curloss = train_event.loss

        # Start solver, we'll context switch to the caffe_root directory because Caffe has issues not being
        # the center of the universe.
        with cd(caffe_root):
            process_args = [caffe_path, 'train', '--solver', solver]
            with subprocess.Popen(process_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
                for line in iter(proc.stderr.readline, b''):
                    logging.debug('[CAFFE OUTPUT ] {0}'.format(line))
                    parsed_event = parse_train_line(line)
                    if parsed_event:
                        _consolidate_training(parsed_event)
                        # If we've already seen all three fields, start sending data
                        if self.curiter and self.curloss and self.curacc:
                            event = TrainingCaffeEvent(self.curiter, self.curloss, self.curacc)
                            self.action_handler.put(event)
                # Wait for completion
                proc.wait(timeout=10)
                code = proc.returncode
        if code != 0:
            logging.error('Caffe returned with non-zero error code! (returned {0})'.format(code))
            raise OSError('Caffe external call failed')
