import uuid
import ydb
import ydb.iam
import os
import json

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
                                  project["title"],
                                  project["description"],
                                  login)
    return {
        'statusCode': 200,
        'body': 'POST /project ' + str(result)
    }


def get_projects(event):
    login = event["requestContext"]["authorizer"]["login"]
    result = get_projects_query(pool, login)
    info = result[0].rows
    return {
        'statusCode': 200,
        'body': string_to_json(str(info))
    }


def update_project(event):
    project_id = event["params"]["id"]
    project = json.loads(event["body"])
    result = upsert_project_query(pool,
                                  project_id,
                                  project["title"],
                                  project["description"])
    return {
        'statusCode': 200,
        'body': 'UPDATE /projects ' + str(result)
    }


def delete_project(event):
    project_id = event["params"]["id"]
    result = delete_project_query(pool, project_id)
    return {
        'statusCode': 200,
        'body': 'DELETE /projects ' + str(result)
    }


def error(event):
    return {
        'statusCode': 400,
        'body': 'Invalid request'
    }


def upsert_project_query(pool, project_id, title, description):
    def callee(session):
        return session.transaction().execute(
            f"UPSERT INTO `projects` (`id`, `description`, `title`) VALUES ('{project_id}', '{description}', '{title}');",
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(10).with_operation_timeout(5)
        )

    return pool.retry_operation_sync(callee)


def create_project_query(pool, title, description, login):
    def callee(session):
        project_id = uuid.uuid4()
        return session.transaction().execute(
            f"UPSERT INTO `projects` (`id`, `description`, `title`) VALUES ('{project_id}', '{description}', '{title}');UPSERT INTO `roles` ( `user_id`, `project_id`, `role` ) VALUES ('{login}','{project_id}','manager');",
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(10).with_operation_timeout(5)
        )

    return pool.retry_operation_sync(callee)


def delete_project_query(pool, project_id):
    def callee(session):
        return session.transaction().execute(
            f"DELETE FROM `projects` WHERE `id` = '{project_id}';DELETE FROM `tasks` WHERE `project_id` = '{project_id}'; DELETE FROM `roles` WHERE `project_id` = '{project_id}';",
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(10).with_operation_timeout(5)
        )

    return pool.retry_operation_sync(callee)


def get_projects_query(pool, login):
    def callee(session):
        return session.transaction().execute(
            f"SELECT `projects`.id, `projects`.title, `projects`.description, `roles`.role FROM `projects` LEFT JOIN `roles` ON `projects`.id = `roles`.project_id WHERE `roles`.user_id = '{login}';",
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(10).with_operation_timeout(5)
        )

    return pool.retry_operation_sync(callee)


def string_to_json(input_string):
    # Remove the single quotes from the input string
    return input_string.replace("b'", "'").replace("'", "\"")
