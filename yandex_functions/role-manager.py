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
    httpMethod = event["httpMethod"]
    project_id = event["params"]["id"]
    if httpMethod == 'GET':
        return get_roles(project_id)
    payload = json.loads(event["body"])
    if httpMethod == 'POST':
        return add_role(payload, project_id)
    elif httpMethod == 'PUT':
        return add_role(payload, project_id)
    elif httpMethod == 'DELETE':
        return delete_role(payload, project_id)
    else:
        return error(event)


def add_role(payload, project_id):
    result = add_role_query(pool,
                            payload["user_id"],
                            project_id,
                            payload["role"])
    return {
        'statusCode': 200,
        'body': 'POST /role: ' + str(result)
    }


def get_roles(project_id):
    result = get_roles_query(pool,
                             project_id)
    return {
        'statusCode': 200,
        'body': string_to_json(str(result[0].rows))
    }


def delete_role(payload, project_id):
    result = delete_role_query(pool,
                               payload["user_id"],
                               project_id)
    return {
        'statusCode': 200,
        'body': 'DELETE /role: ' + str(result)
    }


def error(event):
    return {
        'statusCode': 400,
        'body': 'Invalid request'
    }


def add_role_query(pool, user_id, project_id, role):
    def callee(session):
        return session.transaction().execute(
            f"UPSERT INTO `roles`( `user_id`, `project_id`, `role` ) VALUES ('{user_id}', '{project_id}', '{role}');",
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(10).with_operation_timeout(5)
        )

    return pool.retry_operation_sync(callee)


def get_roles_query(pool, project_id):
    def callee(session):
        return session.transaction().execute(
            f"SELECT `user_id`, `project_id`, `role` FROM `roles` WHERE `project_id` = '{project_id}';",
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(10).with_operation_timeout(5)
        )

    return pool.retry_operation_sync(callee)


def delete_role_query(pool, user_id, project_id):
    def callee(session):
        return session.transaction().execute(
            f"DELETE FROM `roles` WHERE `project_id` = '{project_id}' AND `user_id` = '{user_id}';",
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(10).with_operation_timeout(5)
        )

    return pool.retry_operation_sync(callee)


def string_to_json(input_string):
    # Remove the single quotes from the input string
    return input_string.replace("b'", "'").replace("'", "\"").replace("\"{", "{").replace("}\"", "}").replace(
        "\"\"[]\"\"", "[]")
