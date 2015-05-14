import logging
import requests
import json

from .BaseDispatch import BaseDispatch


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

    def train_event(self, event, event_url='/api/events'):
        """Dispatch training events to the Mri-server via REST interface

        Arguments
        ----------
        event : TrainingCaffeEvent
            Info for this training event

        event_url : string
            URI to send post events to in Mri-server (shouldn't need to change)
        """
        super().train_event(event)
        payload = self._format_train_request(event)
        result = self._send_request(event_url, 'POST', payload)
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
        except requests.ConnectionError as ex:
            logging.warning('Failed to send request because of a network problem')
            logging.warning('Message from exception: {0}'.format(ex))
            return None
        except requests.TimeoutError as ex:
            logging.warning('Failed to send request because the server timed out')
            logging.warning('Message from exception: {0}'.format(ex))
            return None
        return result

    def _create_report(self):
        """Called during init, creates a new report on the server"""
        pass

    def _format_train_request(self, train_event):
        """Generate the payload for the train request"""
        event_type = 'train.{0}'.format(self.task_params['id'].replace(' ', ''))
        properties = {
            'iteration': train_event.iteration,
            'loss': train_event.loss,
            'accuracy': train_event.accuracy
        }
        payload = {
            'type': event_type,
            'properties': properties
        }
        return json.dumps(payload)

    def _post_train_event(self):
        """Called during train event, posts a new training event via HTTP"""
        pass
