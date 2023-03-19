import os
import ydb

# Create driver in global space.
driver = ydb.Driver(endpoint=os.getenv('YDB_ENDPOINT'), database=os.getenv('YDB_DATABASE'))
# Wait for the driver to become active for requests.
driver.wait(fail_fast=True, timeout=5)
# Create the session pool instance to manage YDB sessions.
pool = ydb.SessionPool(driver)


def get_id(session):
    # Create the transaction and execute query.
    return session.transaction().execute(
        'SELECT COUNT(id) FROM `table396`;',
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    )


def create_task(pool, userId):
    taskId = int(pool.retry_operation_sync(get_id)[0].rows[0].column0)

    def callee(session):
        session.transaction().execute(
            "UPSERT INTO `table396` ( `id`, `description`, `title`, `userId` ) VALUES ({}, 'some', 'some', '{}');".format(
                taskId, userId),
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(10).with_operation_timeout(5)
        )

    return pool.retry_operation_sync(callee)


def handler(event, context):
    # Execute query with the retry_operation helper.
    result = create_task(pool, event["params"]["ID"])
    return {
        'statusCode': 200,
        'body': str(result),
    }