from .CaffeEvent import CaffeEvent


class TrainingEvent(CaffeEvent):
    """Container for training events"""
    def __init__(self, iteration, loss, accuracy):
        super().__init__()
        self.iteration = iteration
        self.loss = loss
        self.accuracy = accuracy

    def __str__(self):
        return 'Iter: {0}, Loss: {1}, Acc: {2}'.format(self.iteration, self.loss, self.accuracy)