import requests
import json


def hello_world(event, context):
    google = requests.get('http://finance.google.com/finance/info?q=NASDAQ:GOOG').text
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'message': 'Hello World', 'google': google})
    }
