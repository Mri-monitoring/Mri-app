import unittest
import requests
import json

from Mri.dispatch import MriServerDispatch
from Mri.caffe import TrainingCaffeEvent

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
        data = json.dumps({'introducing' : 'kitton mittons'})
        result = server._send_request('/post', 'POST', data)
        self.assertEqual(result.status_code, 200)
        # Check that we fail gracefully
        server = MriServerDispatch({}, 'http://744.255.255.1', 'test', 'tester')
        result = server._send_request('/get', 'GET', None)
        self.assertEqual(result, None)

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
        event = TrainingCaffeEvent(100, 200, 300)
        data = server._format_train_request(event)
        correct = json.dumps(
            {"type": "train.abcde", "properties": {"iteration": 100, "loss": 200, "accuracy": 300}}
        )
        self.assertEqual(data, correct)

if __name__ == '__main__':
    unittest.main()
