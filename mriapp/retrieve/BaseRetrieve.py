from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()


class BaseRetrieve(object):
    """Base class to retrieve new solver jobs

    Arguments
    ----------
    None
    """
    def __init__(self):
        pass

    def retrieve_task(self):
        """Retrieve the next task and return a json/dict representation. A task
        can contain multiple directives and files to fetch. This is a generator"""
        pass

    def retrieve_file(self, location):
        """Fetch a file and return a json/dict representation"""
        pass