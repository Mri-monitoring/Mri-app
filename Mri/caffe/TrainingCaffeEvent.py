from .BaseCaffeEvent import BaseCaffeEvent


class TrainingCaffeEvent(BaseCaffeEvent):
    """Container for training events"""
    def __init__(self, iteration, loss, accuracy):
        super().__init__()
        if iteration is None:
            raise ValueError('Cannot instantiate a training event without an interation number')
        self.iteration = iteration
        self.loss = loss
        self.accuracy = accuracy

    def __str__(self):
        return 'Iter: {0}, Loss: {1}, Acc: {2}'.format(self.iteration, self.loss, self.accuracy)

    def __eq__(self, other):
        if (
            self.iteration == other.iteration and
            self.loss == other.loss and
            self.accuracy == other.accuracy
        ):
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)