from Mri.utilities import cd
from Mri.event import TrainingEvent
from .helpers import parse_train_line
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

    def train(self, caffe_root, solver, caffe_path='./build/tools/caffe', snapshot=None):
        """Run Caffe training given the required models

        Parameters
        ----------
        caffe_root : string
            Location of the root Caffe folder

        solver : string
            Location of the solver file for this Caffe run

        caffe_path : string
            Location of the actual Caffe executable

        snapshot : string
            If present, location of snapshot file to resume from
        """

        # Start solver, we'll context switch to the caffe_root directory because Caffe has issues not being
        # the center of the universe.
        with cd(caffe_root):
            process_args = [caffe_path, 'train', '--solver', solver]
            # Resume training from snapshot?
            if snapshot:
                process_args.append('--snapshot')
                process_args.append(snapshot)
            with subprocess.Popen(process_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
                for line in iter(proc.stderr.readline, b''):
                    logging.debug('[CAFFE OUTPUT ] {0}'.format(line))
                    parsed_event = parse_train_line(line)
                    if parsed_event:
                        # If we've already seen the iteration, start sending data
                        if 'iteration' in parsed_event:
                            self.curiter = parsed_event['iteration']
                        if self.curiter is not None:
                            parsed_event['iteration'] = self.curiter
                            try:
                                event_struct = TrainingEvent.create_from_dict(parsed_event)
                                self.action_handler.put(event_struct)
                            except ValueError:
                                # We only want to send events that have a field filled out
                                pass

                # Wait for completion
                proc.wait(timeout=10)
                code = proc.returncode
        if code != 0:
            logging.error('Caffe returned with non-zero error code! (returned {0})'.format(code))
            raise OSError('Caffe external call failed')
