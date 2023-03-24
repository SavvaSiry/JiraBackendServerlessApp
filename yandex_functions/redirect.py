import requests
import json
import jwt
import datetime
import ydb
import ydb.iam
import os

# Create driver in global space.
driver = ydb.Driver(
  endpoint=os.getenv('YDB_ENDPOINT'),
  database=os.getenv('YDB_DATABASE'),
  credentials=ydb.iam.MetadataUrlCredentials())
# Wait for the driver to become active for requests.
driver.wait(fail_fast=True, timeout=5)
# Create the session pool instance to manage YDB sessions.
pool = ydb.SessionPool(driver)


def handler(event, context):
    user_tokens = json.loads(get_token_with_code(event["params"]["code"]).text)
    user_info = get_user_info_with_token(user_tokens["access_token"])
    add_user_if_not_exist(pool, user_info["login"], user_info["default_email"], user_info["default_avatar_id"])
    print(user_info)
    response = authorize_user(user_info)
    return {
        'statusCode': 200,
        'body': str(response),
    }


def get_token_with_code(code):
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': 'e78f67c5c3d442599dc19e665bda8543',
        'client_secret': 'c5bb6de9db004bc6bb0b3d34d46916e3'
    }
    return requests.post("https://oauth.yandex.ru/token", params=payload, data=payload)


def get_user_info_with_token(token):
    r = requests.get("https://login.yandex.ru/info?oauth_token=" + token)
    data_dict = json.loads(r.text)
    return data_dict


def authorize_user(user_data):
    login_value = user_data['login']
    now = datetime.datetime.utcnow()
    minutes = 30
    exp = now + datetime.timedelta(minutes=minutes)
    # claims = {'iss': 'my_issuer', 'sub': 'my_subject', 'aud': 'my_audience', 'exp': 0, 'iat': 0,
    #           'login': login_value}
    claims = {'iss': 'my_issuer', 'sub': 'my_subject', 'aud': 'my_audience', 'login': login_value}
    # Generate the JWT token
    secret_key = 'secret_key'
    algorithm = 'HS256'
    jwt_token = jwt.encode(claims, secret_key, algorithm=algorithm)
    response = {
        'access_token': jwt_token,
        'token_type': 'Bearer',
        'expires_in': minutes * 60
    }
    return json.dumps(response)


def add_user_if_not_exist(pool, login, email, icon):
    def callee(session):
        session.transaction().execute(
            "UPSERT INTO `user` ( `login`, `email`, `icon`) VALUES ('{}', '{}', '{}');".format(login, email, icon),
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(10).with_operation_timeout(5)
        )

    return pool.retry_operation_sync(callee)