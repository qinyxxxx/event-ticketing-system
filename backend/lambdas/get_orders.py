def lambda_handler(event, context):
    # TODO
    # - Read userId from query parameters
    # - Query OrdersTable (if GSI exists)
    # - Or scan and filter (short-term demo)
    return {
        "statusCode": 200,
        "body": "TODO: get orders"
    }