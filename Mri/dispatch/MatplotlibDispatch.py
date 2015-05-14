import matplotlib.pyplot as plt
import numpy as np
import logging
import os

from .BaseDispatch import BaseDispatch


class MatplotlibDispatch(BaseDispatch):
    """Display events via Matplotlib backend

    Arguments
    ----------
    task_params : dict
        Dictionary of the task json specification, including name and ID number

    img_folder : string
        Folder to save output images to
    """
    def __init__(self, task_params, img_folder):
        super().__init__()
        self._losses = []
        self._accs = []
        self.task_params = task_params
        self._img_folder = img_folder
        plt.figure(figsize=(12,10))
        plt.ion()
        plt.show()

    def train_event(self, event):
        """Plot a basic training and testing curve via Matplotlib"""
        super().train_event(event)

        # Update list
        if event.accuracy:
            self._accs.append([event.iteration, event.accuracy])
        if event.loss:
            self._losses.append([event.iteration, event.loss])

        # Convert to numpy arrays
        loss = np.array(self._losses)
        acc = np.array(self._accs)

        # Display if we have accuracy and loss
        if loss.size > 0 and acc.size > 0:
            plt.clf()
            plt.plot(loss[:,0], loss[:,1], acc[:,0], acc[:,1])
            plt.ylim([0, 1])
            plt.legend(['Loss', 'Accuracy'], loc='lower left')
            plt.title(self.task_params['name'])
            plt.grid(True, which='both')
            plt.draw()

    def train_finish(self):
        """Save our output figure to PNG format"""
        filename = self.task_params['name'].replace(' ', '_')
        save_path = os.path.join(self._img_folder, filename)
        logging.info('Finished training! Saving output image to {0}'.format(save_path))
        plt.savefig(save_path, bbox_inches='tight')
