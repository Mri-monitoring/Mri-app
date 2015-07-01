from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import unittest
import json

from Mri.dispatch import MriServerDispatch
from Mri.event import TrainingEvent
from Mri.utilities import ServerConsts

HTTP_BIN = 'http://httpbin.org'


class TestMriServerDispatch(unittest.TestCase):
    def setUp(self):
        pass

    def test_basic_requests(self):
        # Check basic functionality
        server = MriServerDispatch({}, HTTP_BIN, 'test', 'tester')
        result = server._send_request('/get', 'GET', None)
        self.assertEqual(result.status_code, 200)
        # Check auth
        server = MriServerDispatch({}, HTTP_BIN, 'test', 'tester')
        result = server._send_request('/basic-auth/test/tester', 'GET', None)
        self.assertEqual(result.status_code, 200)
        # Check post
        server = MriServerDispatch({}, HTTP_BIN, 'test', 'tester')
        data = json.dumps({'introducing': 'kitton mittons'})
        result = server._send_request('/post', 'POST', data)
        self.assertEqual(result.status_code, 200)

    def test_exceptions(self):
        # Check that we gracefully handle failed servers
        server = MriServerDispatch({}, 'http://thiswontworkatall', 'test', 'tester')
        result = server._send_request('/', 'GET', None)
        self.assertEqual(result, None)
        # Check that we fail gracefully on invalid urls
        server = MriServerDispatch({}, 'http://744.255.255.1', 'test', 'tester')
        result = server._send_request('/get', 'GET', None)
        self.assertEqual(result, None)
        # Check that we can detect 404s
        server = MriServerDispatch({}, HTTP_BIN, 'test', 'tester')
        result = server._send_request('/thisisntarealpath', 'GET', None)
        self.assertEqual(result.status_code, 404)

    def test_new_report(self):
        server = MriServerDispatch({'name': 'test'}, HTTP_BIN, 'test', 'tester')
        old = ServerConsts.API_URL.REPORT
        ServerConsts.API_URL.REPORT = '/post'
        result = server._new_report()
        ServerConsts.API_URL.REPORT = old
        self.assertEqual(result['data'], '{"title": "test"}')

    def test_format_train_request(self):
        server = MriServerDispatch({'name': 'test', 'id': 'cbdcig'}, HTTP_BIN, 'test', 'tester')
        event = TrainingEvent({'iteration': 100, 'loss': 0.5, 'accuracy': 0.6}, 'iteration')
        payload = server._format_train_request(event)
        self.assertTrue('train.cbdcig' in payload)
        self.assertTrue('"accuracy": 0.6' in payload)

    def test_format_report(self):
        server = MriServerDispatch({'name': 'test', 'id': 'cbdcig'}, HTTP_BIN, 'test', 'tester')
        # Save const states
        old_id = ServerConsts.API_URL.REPORT_ID
        old = ServerConsts.API_URL.REPORT
        ServerConsts.API_URL.REPORT_ID = '/put'
        ServerConsts.API_URL.REPORT = '/post'

        # Test
        result = server.setup_display('iteration', ['iteration', 'loss', 'accuracy'])
        obj = json.loads(result.text)['json']

        # Restore states
        ServerConsts.API_URL.REPORT = old
        ServerConsts.API_URL.REPORT_ID = old_id

        self.assertEqual('big', obj['visualizations'][0]['configuration']['size'])
        self.assertEqual('train.cbdcig', obj['visualizations'][0]['eventName'])

    def test_train_event(self):
        # Check post
        server = MriServerDispatch({}, HTTP_BIN, 'test', 'tester')
        data = json.dumps(
            {"type": "train.abcde", "properties": {"iteration": 100, "loss": 200, "accuracy": 300}}
        )
        result = server._send_request('/post', 'POST', data)
        self.assertEqual(result.status_code, 200)
        self.assertTrue('train.abcde' in result.text)

    def test_formatting(self):
        server = MriServerDispatch({'id': 'abcde'}, HTTP_BIN, 'test', 'tester')
        event = TrainingEvent({'iteration': 100, 'loss': 200, 'accuracy': 300}, 'iteration')
        data = server._format_train_request(event)
        correct = json.dumps(
            {"type": "train.abcde", "properties": {"iteration": 100, "loss": 200, "accuracy": 300}}
        )
        self.assertEqual(data, correct)

if __name__ == '__main__':
    unittest.main()
