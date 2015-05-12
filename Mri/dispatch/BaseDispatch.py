import logging

class BaseDispatch(object):
    """Base class to dispatch new actions to whatever backend you want

    Arguments
    ----------
    None
    """
    def __init__(self):
        pass

    def train_event(self, event):
        """Parse a line of output from a training caffe object"""
        logging.debug(event)