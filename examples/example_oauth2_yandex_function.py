import requests
import json

def handler(event, context):
    payload = {
        'grant_type': 'authorization_code',
        'code': str(event["params"]["code"]),
        'client_id': 'e78f67c5c3d442599dc19e665bda8543',
        'client_secret': 'c5bb6de9db004bc6bb0b3d34d46916e3'
    }
    r = requests.post("https://oauth.yandex.ru/token", params=payload, data=payload)
    userTokens = json.loads(r.text)
    userInfo = requests.get("https://login.yandex.ru/info?oauth_token=" + userTokens["access_token"])
    return {
        'statusCode': 200,
        'headers': {'Location': 'https://www.google.com/'},
        'body': str(userInfo.text),
    }