from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import logging

class BaseDispatch(object):
    """Base class to dispatch new actions to whatever backend you want

    Arguments
    ----------
    None
    """
    def __init__(self):
        pass

    def setup_display(self):
        """Create whatever front end we're using"""
        logging.debug('New display being created for dispatcher')

    def train_event(self, event):
        """Parse a line of output from a training caffe object"""
        logging.debug(event)

    def train_finish(self):
        """Call once training is finished"""
        logging.debug('Training finished!')
