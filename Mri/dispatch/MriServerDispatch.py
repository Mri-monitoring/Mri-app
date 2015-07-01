from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import super
from future import standard_library
standard_library.install_aliases()
import logging
import requests
import json

from .BaseDispatch import BaseDispatch
from Mri.utilities import ServerConsts


class MriServerDispatch(BaseDispatch):
    """Display events via the Mri-Server front-end. For this dispatch, we will treat
    each task as a separate report. There may be multiple visualizations on the server
    for a report, and there may be multiple directives in a task. These two, however, aren't
    necessarily bijective.

    Arguments
    ----------
    task_params : dict
        Dictionary of the task json specification, including name and ID number

    address : string
        Server address, generally a hosted URL

    username : string
        Username for the Mri-server

    password : string
        Password for the Mri-server
    """
    def __init__(self, task_params, address, username, password):
        super().__init__()
        self.task_params = task_params
        self.address = address
        self.auth = (username, password)
        self.report_id = None

    def setup_display(self, time_axis, attributes):
        """Create a report for this dispatch, usually done at init

        Arguments
        ----------
        time_axis : string
            Name of attribute representing time eg. iterations, epoch, etc

        attributes : list
            List of strings representing attributes to plot eg. loss, accuracy,
            learning rate, etc. If time_axis attribute is present it will be ignored.
        """
        super().setup_display(time_axis, attributes)
        report_json = self._new_report()
        if 'id' in report_json:
            self.report_id = report_json['id']
        elif 'data' in report_json:
            # This is for unit testing
            self.report_id = ''
        return self._format_report()

    def train_event(self, event):
        """Dispatch training events to the Mri-server via REST interface

        Arguments
        ----------
        event : TrainingEvent
            Info for this training event

        event_url : string
            URI to send post events to in Mri-server (shouldn't need to change)
        """
        super().train_event(event)
        payload = self._format_train_request(event)
        result = self._send_request(ServerConsts.API_URL.EVENT, 'POST', payload)
        return result

    def train_finish(self):
        """Final call for training, can be used to issue alerts/etc"""
        pass

    def _send_request(self, suffix, protocol, data):
        """Send a report via HTTP, but allow for non-responsive or dead servers

        Arguments
        ----------
        suffix : string
            URL suffix for this request

        protocol : string
            Type of request to make (GET, POST, PUT, etc)

        data : dict
            JSON object of data to pass in request

        Returns
        ----------
        result : requests.Response
            Response from the webpage, includes response code, encoding, and text
        """
        headers = {'Content-Type': 'application/json'}
        try:
            protocol = protocol.upper()
            url = requests.compat.urljoin(self.address, suffix)
            result = requests.request(method=protocol, url=url, data=data, headers=headers, auth=self.auth)
            logging.info('Sent request, result {0}'.format(result.status_code))
            if result.status_code != 200:
                logging.warning('Request not 200, server says {0}'.format(result.text))
        except requests.exceptions.ConnectionError as ex:
            logging.warning('Failed to send request because of a network problem')
            logging.warning('Message from exception: {0}'.format(ex))
            return None
        except requests.exceptions.ConnectTimeout as ex:
            logging.warning('Failed to send request because the server timed out')
            logging.warning('Message from exception: {0}'.format(ex))
            return None
        return result

    def _format_report(self):
        """Called after creating a new report, formats a report to display Mri events"""
        if not self.setup:
            raise ValueError('Dispatch not setup yet, please call setup_report')
        full_url = requests.compat.urljoin(ServerConsts.API_URL.REPORT_ID, self.report_id)
        # Compile fields, etc
        attr_no_time = self._attributes
        attr_no_time.remove(self._time_axis)
        fields = ','.join(attr_no_time)
        scales = ','.join(['auto'] * len(attr_no_time))
        sample = self._time_axis

        # Add training visualizations
        payload = json.dumps({
            'title': self.task_params['name'],
            'visualizations': [
                {
                    'type': 'plot',
                    'eventName': 'train.'+self.task_params['id'],
                    'configuration': {
                        'title': 'Training Progress',
                        'sample': sample,
                        'fields': fields,
                        'scales': scales,
                        'limit': 100000,
                        'size': 'big',
                        'interpolation': 'linear'
                    }
                }
            ]
        })
        result = self._send_request(full_url, 'PUT', payload)
        return result

    def _new_report(self):
        """Called during init, creates a new report on the server and returns its ID"""
        payload = json.dumps({'title': self.task_params['name']})
        result = self._send_request(ServerConsts.API_URL.REPORT, 'POST', payload).text
        result_obj = json.loads(result)
        return result_obj

    def _format_train_request(self, train_event):
        """Generate the payload for the train request"""
        event_type = 'train.{0}'.format(self.task_params['id'].replace(' ', ''))
        properties = train_event.attributes
        payload = {
            'type': event_type,
            'properties': properties
        }
        return json.dumps(payload)
