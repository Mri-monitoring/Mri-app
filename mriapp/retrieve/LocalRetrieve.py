from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import super
from builtins import open
from future import standard_library
standard_library.install_aliases()
import logging
import json


class LocalRetrieve(object):
    """Retrieve new solver jobs from local filesystem

    Arguments
    ----------
    task_record : string
        File on the local system containing a list of folders with tasks
    """
    def __init__(self, task_record):
        super().__init__()
        self.task_record = task_record
        self._f = open(task_record)

    def __del__(self):
        """Make sure we close our file on object deletion"""
        if not self._f.closed:
            self._f.close()

    def retrieve_task(self):
        """Retrieve the next task and return a json/dict representation.

        A task can contain a number of directives, but will generally contain
        the training task for Caffe, including the locations of model/solvers.
        This function is a generator and will allow iteration through the entire
        set of possible tasks.
        """
        for next_line in self._f.read().splitlines():
            logging.debug(next_line)
            if next_line:
                try:
                    with open(next_line) as js:
                        item = json.load(js)
                        yield item
                except FileNotFoundError as e:
                    logging.warning('Failed to find retrieve task file')
                    logging.warning(e.strerror)

    def retrieve_file(self, location):
        """Basically the identity function - we don't need to get any network data
        for local files, so we'll just pass back the file handle"""
        return location
