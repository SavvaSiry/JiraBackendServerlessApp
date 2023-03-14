import jwt
import json
import unittest
import datetime


# Define function that retrieves login field from JSON and creates JWT token
def authorize_user(user_data):
    data_dict = json.loads(user_data)
    login_value = data_dict['login']
    now = datetime.datetime.utcnow()
    minutes = 30
    exp = now + datetime.timedelta(minutes=minutes)
    claims = {'iss': 'my_issuer', 'sub': 'my_subject', 'aud': 'my_audience', 'exp': 0, 'iat': 0,
              'login': login_value}
    # Generate the JWT token
    secret_key = 'secret_key'
    algorithm = 'HS256'
    jwt_token = jwt.encode(claims, secret_key, algorithm=algorithm)
    request = {
        'access_token': jwt_token,
        'token_type': 'Bearer',
        'expires_in': minutes * 60
    }
    return request


def create_jwt_token(json_data):
    login = json_data.get('login')
    if login is None:
        raise ValueError('Login field is missing')
    # Set JWT token with login claim
    claims = {'iss': 'my_issuer', 'sub': 'my_subject', 'aud': 'my_audience', 'exp': 0, 'iat': 0,
              'login': login}
    token = jwt.encode(claims, 'secret_key', algorithm='HS256')
    return token


# Define test case class
class TestCreateJWTToken(unittest.TestCase):

    # Test case for valid input
    def test_create_jwt_token_valid(self):
        json_data = '{"id": "1000067278", "login": "savvasiriy", "client_id": "e78f67c5c3d442599dc19e665bda8543", "display_name": "savvasiriy", "real_name": "\u0421\u0430\u0432\u0432\u0430 \u0421\u0438\u0440\u044b\u0439", "first_name": "\u0421\u0430\u0432\u0432\u0430", "last_name": "\u0421\u0438\u0440\u044b\u0439", "sex": "male", "default_email": "savvasiriy@yandex.ru", "emails": ["savvasiriy@yandex.ru"], "default_avatar_id": "54535/m2YVJQvmyWxqqr2zeOlfivoZzRg-1", "is_avatar_empty": false, "psuid": "1.AAk7QA.cMxkC56DH8yRTXecS0-RsA.Y0A5caPzfKSnbrHytobaZw"}'
        expected_token = create_jwt_token({'login': 'savvasiriy'})
        actual_token = authorize_user(str(json_data))
        print(actual_token)
        self.assertEqual(actual_token.get('access_token'), expected_token)


if __name__ == '__main__':
    unittest.main()
