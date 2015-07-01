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
        self._time_axis = ''
        self._attributes = []
        self.setup = False
        pass

    def setup_display(self, time_axis, attributes):
        """Create whatever front end we're using"""
        logging.debug('New display being created for dispatcher')

        # Save time-axis and attributes
        if time_axis not in attributes:
            raise ValueError('Attributes must contain the time-axis attribute')
        self._time_axis = time_axis
        self._attributes = attributes
        logging.debug('New display with time axis {0} and attributes {1}'.format(time_axis, attributes))
        self.setup = True

    def train_event(self, event):
        """Parse a line of output from a training caffe object"""
        logging.debug(event)
        if not self.setup:
            raise ValueError('Dispatch has not been setup -- call setup_display first')

        if event.time_axis != self._time_axis:
            raise ValueError('Time-axis mismatch between dispatch and event')

        event_set = set(event.attributes.keys())
        dispatch_set = set(self._attributes)
        if not event_set.intersection(dispatch_set):
            raise ValueError('Events must contain at least one attribute present in this dispatch')

    def train_finish(self):
        """Call once training is finished"""
        if not self.setup:
            raise ValueError('Dispatch has not been setup -- call setup_display first')
        logging.debug('Training finished!')
