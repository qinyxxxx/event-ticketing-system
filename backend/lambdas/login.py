def lambda_handler(event, context):
    # TODO
    # - Parse body userId/password
    # - No auth needed for demo: always return mock token
    return {
        "statusCode": 200,
        "body": "TODO: login"
    }