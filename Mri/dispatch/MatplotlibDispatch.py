import matplotlib.pyplot as plt
import numpy as np
import logging

from .BaseDispatch import BaseDispatch


class MatplotlibDispatch(BaseDispatch):
    """Display events via Matplotlib backend

    Arguments
    ----------
    task_params : dict
        Dictionary of the task json specification, including name and ID number
    """
    def __init__(self, task_params):
        super().__init__()
        self._iters = []
        self._losses = []
        self._accs = []
        self.task_params = task_params
        plt.figure(figsize=(12,10))
        plt.ion()
        plt.show()

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
        plt.clf()
        plt.plot(iters, loss, iters, acc)
        plt.ylim([0, 1])
        plt.legend(['Loss', 'Accuracy'], loc='lower left')
        plt.title(self.task_params['name'])
        plt.grid(True)
        plt.draw()

    def train_finish(self, filename):
        """Save our output figure to PNG format

        Arguments
        ----------
        filename : string
            Filename to save training curves after completed
        """
        logging.info('Finished training! Saving output image to {0}'.format(filename))
        plt.savefig(filename, bbox_inches='tight')
