import datetime
import uuid
import ydb
import os
import json

# Create driver in global space.
driver = ydb.Driver(endpoint=os.getenv('YDB_ENDPOINT'), database=os.getenv('YDB_DATABASE'))
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
    if httpMethod == 'POST':
        return create_project(event)
    elif httpMethod == 'GET':
        return get_projects(event)
    elif httpMethod == 'PUT':
        return update_project(event)
    elif httpMethod == 'DELETE':
        return delete_project(event)
    else:
        return error(event)


def create_project(event):
    project = json.loads(event["body"])
    login = event["requestContext"]["authorizer"]["login"]
    result = create_project_query(pool,
                                  login,
                                  project["title"],
                                  project["description"])
    return {
        'statusCode': 200,
        'body': 'GET /tasks ' + str(result)
    }


def get_projects(event):
    login = event["requestContext"]["authorizer"]["login"]
    result = get_projects_query(pool, login)
    return {
        'statusCode': 200,
        'body': 'GET /tasks ' + str(result)
    }


def update_project(event):
    id_param = event["params"]["id"]
    project = json.loads(event["body"])
    login = event["requestContext"]["authorizer"]["login"]
    result = upsert_project_query(pool,
                                  id_param,
                                  project["title"],
                                  project["description"],
                                  login)
    return {
        'statusCode': 200,
        'body': 'GET /tasks ' + str(result)
    }


def delete_project(event):
    id_param = event["params"]["id"]
    result = delete_project_query(pool, id_param)
    return {
        'statusCode': 200,
        'body': 'GET /tasks ' + str(result)
    }


def error(event):
    return {
        'statusCode': 400,
        'body': 'Invalid request'
    }


def create_project_query(pool, login, title, description):
    return upsert_project_query(pool, uuid.uuid4(), title, description, login)


def upsert_project_query(pool, project_id,  title, description, login):
    def callee(session):
        return session.transaction().execute(
            "UPSERT INTO `projects` (`id`, `description`, `manager`, `title`) VALUES ( '{}', '{}', '{}', '{}');".format(project_id, description, login, title),
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(10).with_operation_timeout(5)
        )

    return pool.retry_operation_sync(callee)


def delete_project_query(pool, project_id):
    def callee(session):
        return session.transaction().execute(
            "DELETE FROM `projects` WHERE `id` = '{}';".format(project_id),
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(10).with_operation_timeout(5)
        )

    return pool.retry_operation_sync(callee)


def get_projects_query(pool, login):
    def callee(session):
        return session.transaction().execute(
            "SELECT `id`, `description`, `manager`, `title` FROM `projects` WHERE `manager` = '{}';".format(login),
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(10).with_operation_timeout(5)
        )

    return pool.retry_operation_sync(callee)


def string_to_json(input_string):
    # Remove the single quotes from the input string
    return input_string.replace("b'", "'").replace("'", "\"")
