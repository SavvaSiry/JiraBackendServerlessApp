import requests

def handler(event, context):
    payload = {
        'grant_type': 'authorization_code',
        'code': str(event["params"]["code"]),
        'client_id': '',
        'client_secret': ''
    }
    r = requests.post("https://oauth.yandex.ru/token", params=payload, data=payload)
    return {
        'statusCode': 200,
        'headers': {'Location': 'https://www.google.com/'},
        'body': str(r.text),
    }