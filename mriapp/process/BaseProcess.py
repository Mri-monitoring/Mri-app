from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()


class BaseProcess(object):
    """Base class for processes like solving

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
        self.directive = directive_params
        self.config = config
        self.action_handler = action_handler

    def train(self):
        pass

    def test(self):
        pass

    @property
    def alive(self):
        return False