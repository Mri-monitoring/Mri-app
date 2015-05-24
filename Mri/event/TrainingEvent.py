from Mri.event import BaseEvent


class TrainingEvent(BaseEvent):
    """Container for training events. Training events must have an iteration, and must
    have at least one other attribute to be valid"""
    def __init__(self, iteration, loss, accuracy):
        super().__init__()
        if iteration is None:
            raise ValueError('Cannot instantiate a training event without an iteration number')
        if not loss and not accuracy:
            raise ValueError('Cannot instantiate a training event without a valid field')

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

    @staticmethod
    def create_from_dict(event):
        iteration = None
        loss = None
        acc = None
        if 'iteration' in event:
            iteration = event['iteration']
        if 'loss' in event:
            loss = event['loss']
        if 'accuracy' in event:
            acc = event['accuracy']
        return TrainingEvent(iteration, loss, acc)
