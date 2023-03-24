import uuid
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
    path = event["path"]
    httpMethod = event["httpMethod"]

    if path == '/tasks':
        if httpMethod == 'POST':
            return create_task(event)
        # elif httpMethod == 'GET':
        #     return get_tasks(event)

    elif path == '/tasks/{id}':
        id_param = event["params"]["id"]
        if httpMethod == 'GET':
            return get_tasks(event, id_param)
        elif httpMethod == 'PUT':
            return update_task(event, id_param)
        elif httpMethod == 'DELETE':
            return delete_task(event, id_param)
    else:
        return error(event)


def create_task(event):
    task = json.loads(event["body"])
    result = create_task_query(pool,
                               event["requestContext"]["authorizer"]["login"],
                               task["deadline"],
                               task["description"],
                               task["project_id"],
                               task["status"],
                               task["title"],
                               task["users"])

    return {
        'statusCode': 200,
        'body': 'POST /tasks: ' + str(result)
    }


def get_tasks(event, id_param):
    result = get_tasks_query(pool, id_param)
    return {
        'statusCode': 200,
        'body': string_to_json(str(result[0].rows))
    }


def update_task(event, id_param):
    task = json.loads(event["body"])
    result = upsert_task_query(pool,
                               id_param,
                               event["requestContext"]["authorizer"]["login"],
                               task["deadline"],
                               task["description"],
                               task["project_id"],
                               task["status"],
                               task["title"],
                               json.dumps(task["users"]))
    return {
        'statusCode': 200,
        'body': 'PUT /tasks/{id} ' + str(result)
    }


def delete_task(event, id_param):
    # task = json.loads(event["body"])
    result = delete_task_query(pool, id_param)
    return {
        'statusCode': 200,
        'body': 'DELETE /tasks/{id} ' + str(result)
    }


def error(event):
    return {
        'statusCode': 400,
        'body': 'Invalid request'
    }


def create_task_query(pool, creator, deadline, description, project_id, status, title, users):
    return upsert_task_query(pool, uuid.uuid4(), creator, deadline, description, project_id, status, title,
                             json.dumps(users))


def upsert_task_query(pool, task_id, creator, deadline, description, project_id, status, title, users):
    def callee(session):
        return session.transaction().execute(
            "UPSERT INTO `tasks` ( `id`, `creator`, `deadline`, `description`, `project_id`, `status`, `title`, `users`) VALUES ('{}', '{}', CAST({} as Datetime), '{}', '{}', '{}', '{}', CAST(@@{}@@ as Json));".format(
                task_id, creator, deadline, description, project_id, status, title, users),
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(10).with_operation_timeout(5)
        )

    return pool.retry_operation_sync(callee)


def delete_task_query(pool, task_id):
    def callee(session):
        return session.transaction().execute(
            "DELETE FROM `tasks` WHERE `id` = '{}';".format(task_id),
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(10).with_operation_timeout(5)
        )

    return pool.retry_operation_sync(callee)


def get_tasks_query(pool, project_id):
    def callee(session):
        return session.transaction().execute(
            "SELECT * FROM `tasks` WHERE `project_id` = '{}';".format(
                project_id),
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(10).with_operation_timeout(5)
        )

    return pool.retry_operation_sync(callee)


def string_to_json(input_string):
    # Remove the single quotes from the input string
    return input_string.replace("b'", "'").replace("'", "\"").replace("\"{", "{").replace("}\"", "}").replace("\"\"[]\"\"", "[]")