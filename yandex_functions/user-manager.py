import ydb
import ydb.iam
import os
import json

driver = ydb.Driver(
    endpoint=os.getenv('YDB_ENDPOINT'),
    database=os.getenv('YDB_DATABASE'),
    credentials=ydb.iam.MetadataUrlCredentials())
# Wait for the driver to become active for requests.
driver.wait(fail_fast=True, timeout=5)
# Create the session pool instance to manage YDB sessions.
pool = ydb.SessionPool(driver)


def handler(event, context):
    print(event)
    result = use_function(event, context)
    return {
        'statusCode': result["statusCode"],
        'body': result["body"]
    }


def use_function(event, context):
    user_id = event["requestContext"]["authorizer"]["login"]
    return get_user(user_id)


def get_user(user_id):
    result = get_user_query(pool, user_id)
    return {
        'statusCode': 200,
        'body': string_to_json(str(result[0].rows))
    }


def get_user_query(pool, user_id):
    def callee(session):
        return session.transaction().execute(
            f"SELECT * FROM `user` WHERE `login` = '{user_id}'",
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(10).with_operation_timeout(5)
        )
    return pool.retry_operation_sync(callee)


def string_to_json(input_string):
    # Remove the single quotes from the input string
    return input_string.replace("b'", "'").replace("'", "\"").replace("\"{", "{").replace("}\"", "}").replace("\"\"[]\"\"", "[]")