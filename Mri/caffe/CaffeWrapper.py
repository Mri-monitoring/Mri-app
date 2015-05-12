from Mri.utilities import cd
from .helpers import parse_train_line
from .TrainingEvent import TrainingEvent
import subprocess


class CaffeWrapper(object):
    """Parse and send output from Caffe to ActionDispatch

    Parameters
    ----------
    action_handler : ActionDispatch
        ActionDispatch that handles Caffe actions
    """

    def __init__(self, action_handler):
        self.action_handler = action_handler
        self.curiter = None
        self.curloss = None
        self.curacc = None

    def solve(self, caffe_root, solver):
        """Run Caffe training given the required models

        Parameters
        ----------
        caffe_root : string
            Location of the root Caffe folder

        solver: string
            Location of the solver file for this Caffe run
        """
        # Start solver, we'll context switch to the caffe_root directory because Caffe has issues not being
        # the center of the universe.
        with cd(caffe_root):
            process_args = ['./build/tools/caffe', 'train', '--solver', solver]
            with subprocess.Popen(process_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
                for line in proc.stderr:
                    parsed_event = parse_train_line(line)
                    if parsed_event:
                        self._consolidate_training(parsed_event)
                        # If we've already seen all three fields, start sending data
                        if self.curiter and self.curloss and self.curacc:
                            event = TrainingEvent(self.curiter, self.curloss, self.curacc)
                            self.action_handler.train_event(event)

    def _consolidate_training(self, train_event):
        """Combine traning event with known data"""
        if train_event:
            if train_event.accuracy:
                self.curacc = train_event.accuracy
            if train_event.iteration:
                self.curiter = train_event.iteration
            if train_event.loss:
                self.curloss = train_event.loss