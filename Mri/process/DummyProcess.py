class DummyProcess(object):
    """Dummy process for unit testing

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
        self.iterations_remaining = 100

    def train(self):
        pass

    def test(self):
        pass

    @property
    def alive(self):
        if self.iterations_remaining:
            self.iterations_remaining -= 1
            return True
        else:
            return False