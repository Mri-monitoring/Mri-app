from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import super
from future import standard_library
standard_library.install_aliases()
from Mri.event import BaseEvent


class TrainingEvent(BaseEvent):
    """Container for training events. Training events must have a time-axis variable, and must
    have at least one other attribute to be valid

    Arguments
    ----------
    time_axis : string
        Defines which attribute represents time (eg iteration number or epoch, etc)

    attributes : dict
        Dictonary of attributes for this training event. Must include the time axis attribute and at least one other

    """
    def __init__(self, attributes, time_axis):
        super().__init__()
        if time_axis not in attributes:
            raise ValueError('Training events must contain the time axis attribute')
        if len(attributes) < 2:
            raise ValueError('Training events must contain at least one non-time axis attribute')

        self.time_axis = time_axis
        self.attributes = attributes

    def __str__(self):
        axis = self.time_axis
        axis_val = self.attributes[self.time_axis]
        remaining = dict(self.attributes)
        remaining.pop(self.time_axis)
        return '{0}: {1}, Attributes: {2}'.format(axis, axis_val, remaining)

    def __eq__(self, other):
        if (
            self.attributes == other.attributes and
            self.time_axis == other.time_axis
        ):
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
