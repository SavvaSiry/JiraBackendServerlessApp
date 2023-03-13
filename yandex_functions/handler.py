import requests
import jwt


def handler(event, context):
    r = requests.get('https://jsonplaceholder.typicode.com/todos/1')
    result = use_function(event, context)
    return {
        'statusCode': 200,
        'body': str(r.text),
    }


def use_function(event, context):
    path = event["url"]
    if path == '/path1':
        return function1(event)
    elif path == '/path2':
        return function2(event)
    else:
        return function3(event)


def function1(event):
    return

def function2(event):
    return

def function3(event):
    return
