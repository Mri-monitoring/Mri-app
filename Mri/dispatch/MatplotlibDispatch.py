import matplotlib.pyplot as plt
import numpy as np

from .ActionDispatch import ActionDispatch


class MatplotlibDispatch(ActionDispatch):
    """Display events via Matplotlib backend

    Arguments
    ----------
    None
    """
    def __init__(self):
        super().__init__()
        self._iters = []
        self._losses = []
        self._accs = []
        plt.figure()

    def train_event(self, event):
        """Plot a basic training and testing curve via Matplotlib"""
        super().train_event(event)

        # Update lists
        self._iters.append(event.iteration)
        self._losses.append(event.loss)
        self._accs.append(event.accuracy)

        # Convert to numpy arrays
        iters = np.array(self._iters)
        loss = np.array(self._losses)
        acc = np.array(self._accs)

        # Display
        plt.plot(iters, loss, iters, acc)
        plt.draw()
