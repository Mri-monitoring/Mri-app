from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import super
from future import standard_library
standard_library.install_aliases()
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
        # Data will be a dictionary of lists
        self._data = {}
        self.task_params = task_params
        self._img_folder = img_folder

    def setup_display(self, time_axis, attributes):
        super().setup_display(time_axis, attributes)
        # Setup data
        for item in self._attributes:
            if item != self._time_axis:
                self._data[item] = []
        # Setup plotting
        plt.figure(figsize=(12, 10))
        plt.ion()
        plt.show()

    def train_event(self, event):
        """Plot a basic training and testing curve via Matplotlib"""
        super().train_event(event)

        time = event.attributes[event.time_axis]
        for item in event.attributes:
            if item != event.time_axis:
                val = event.attributes[item]
                self._data[item].append([time, val])

        # Convert to numpy arrays
        np_data = []
        for key in self._data:
            if self._data[key]:
                data = np.array(self._data[key])
                np_data.append(data[:, 0])
                np_data.append(data[:, 1])

        plt.clf()
        plt.plot(*np_data)
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
