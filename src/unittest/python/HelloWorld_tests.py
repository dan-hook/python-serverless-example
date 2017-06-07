import unittest
import HelloWorld
import json


class HelloWorldTests(unittest.TestCase):
    def test_hello_world(self):
        response = HelloWorld.hello_world(None, None)
        self.assertEqual(200, response['statusCode'])
        body = json.loads(response['body'])
        self.assertEqual('Hello World', body['message'])
        self.assertIsInstance(body['google'], ''.__class__)
