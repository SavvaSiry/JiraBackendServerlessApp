import json
import jwt
import time


def handler(event, context):
    response = {
        "isAuthorized": False
    }
    token_info = decode_token(event["headers"]["Authorization"])
    if (token_info):
        response = {
            "isAuthorized": True,
            "context": token_info
        }

    return response


def decode_token(auth_header):
    # try:
    # Get jwt from header
    jwt_token = auth_header.split(" ")[1]
    print(jwt_token)
    # Decode token
    secret_key = 'secret_key'
    decoded_token = jwt.decode(jwt_token, secret_key, audience="my_audience", algorithms=["HS256"])
    # Check expire time
    # current_time = int(time.time())
    # if "exp" in decoded_token and decoded_token["exp"] < current_time:
    # raise Exception("Token has expired")

    return decoded_token

# except jwt.InvalidTokenError:
#     raise Exception("Invalid token")