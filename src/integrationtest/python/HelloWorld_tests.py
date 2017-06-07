import boto3
import requests
import unittest
import os


class HelloWorldTests(unittest.TestCase):

    stack_outputs = None

    def get_stack_outputs(self):
        if self.stack_outputs is None:
            stack_name = "python-serverless-example-{}".format(os.getenv('SERVERLESS_STAGE',
                                                               '{}dev'.format(os.environ['USER'])))

            cf_client = boto3.session.Session(region_name='us-east-1').client('cloudformation')
            self.stack_outputs = dict()
            for output in cf_client.describe_stacks(StackName=stack_name)['Stacks'][0]['Outputs']:
                self.stack_outputs[output['OutputKey']] = output['OutputValue']
        return self.stack_outputs

    def test_hello_world(self):
        result = requests.get('/'.join([self.get_stack_outputs()['ServiceEndpoint'], 'helloworld']),
                              headers={'Content-Type': 'application/json'})
        self.assertEqual(200, result.status_code)
        body = result.json()
        self.assertEqual('Hello World', body['message'])
        self.assertIsInstance(body['google'], ''.__class__)


if __name__ == '__main__':
    unittest.main()
