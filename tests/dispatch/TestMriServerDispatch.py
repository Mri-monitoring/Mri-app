import unittest
import requests
import json

from Mri.dispatch import MriServerDispatch

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


if __name__ == '__main__':
    unittest.main()
