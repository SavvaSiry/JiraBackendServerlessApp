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
        elif httpMethod == 'GET':
            return get_tasks(event)

    elif path == '/tasks/{id}':
        id_param = event["params"]["id"]
        if httpMethod == 'GET':
            return get_task(event, id_param)
        elif httpMethod == 'PUT':
            return update_task(event, id_param)
        elif httpMethod == 'DELETE':
            return delete_task(event, id_param)
    else:
        return error(event)


def create_task(event):
    return {
        'statusCode': 200,
        'body': 'POST /tasks'
    }


def get_tasks(event):
    return {
        'statusCode': 200,
        'body': 'GET /tasks'
    }


def get_task(event, id_param):
    return {
        'statusCode': 200,
        'body': 'GET /tasks/{id} ' + id_param
    }


def update_task(event, id_param):
    return {
        'statusCode': 200,
        'body': 'PUT /tasks/{id} ' + id_param
    }


def delete_task(event, id_param):
    return {
        'statusCode': 200,
        'body': 'DELETE /tasks/{id} ' + id_param
    }


def error(event):
    return {
        'statusCode': 400,
        'body': 'Invalid request'
    }
