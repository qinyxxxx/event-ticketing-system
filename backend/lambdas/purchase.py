def lambda_handler(event, context):
    # TODO
    # - Parse body: userId, eventId, quantity
    # - DynamoDB conditional update:
    #   remainingTickets >= quantity
    # - If success:
    #   - Create order item in OrdersTable
    #   - Send SQS message (order created)
    # - Return success or error
    return {
        "statusCode": 200,
        "body": "TODO: purchase"
    }