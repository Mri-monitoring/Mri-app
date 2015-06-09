from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import super
from future import standard_library
standard_library.install_aliases()
import subprocess
import logging

from Mri.utilities import parse_caffe_train_line, cd
from Mri.event import TrainingEvent
from .BaseProcess import BaseProcess


class CaffeProcess(BaseProcess):
    """Class for running Caffe

    Arguments
    ----------
    directive_params : dict
        Dictionary from the JSON directive parameters

    config : dict
        Dictionary of configuration options

    action_handler : Queue
        Thread-safe queue that transfers events across threads
    """
    def __init__(self, directive_params, config, action_handler):
        super().__init__(directive_params, config, action_handler)
        self.curiter = 0
        self.training = False

    def train(self):
        # Start solver, we'll context switch to the caffe_root directory because Caffe has issues not being
        # the center of the universe.
        self.training = True
        with cd(self.config.get('mri-client', 'caffe_root')):
            caffe_path = self.config.get('mri-client', 'caffe_bin')
            process_args = [caffe_path, 'train', '--solver', self.directive['local_solver']]
            # Resume training from snapshot?
            if 'resume' in self.directive:
                process_args.append('--snapshot')
                process_args.append(self.directive['resume'])
            try:
                proc = subprocess.Popen(process_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                for raw_line in iter(proc.stderr.readline, b''):
                    line = raw_line.replace('\n', '')
                    logging.debug('[CAFFE OUTPUT ] {0}'.format(line))
                    parsed_event = parse_caffe_train_line(line)
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
                proc.wait()
                code = proc.returncode
                self.training = False
            except Exception as e:
                raise e
            finally:
                pass
        if code != 0:
            logging.error('Caffe returned with non-zero error code! (returned {0})'.format(code))
            raise OSError('Caffe external call failed')

    def test(self):
        pass

    @property
    def alive(self):
        return self.training
