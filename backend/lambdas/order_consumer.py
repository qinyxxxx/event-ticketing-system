import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table(os.environ['ORDERS_TABLE'])

def lambda_handler(event, context):
    """
    SQS event consumer Lambda
    Processes order-created messages and updates order status to confirmed
    """
    records_processed = 0
    records_failed = 0
    
    for record in event.get('Records', []):
        try:
            # Parse SQS message body
            message_body = json.loads(record['body'])
            order_id = message_body.get('orderId')
            
            if not order_id:
                print(f"Error: Missing orderId in message: {message_body}")
                records_failed += 1
                continue
            
            # Update order status from pending to confirmed
            orders_table.update_item(
                Key={'orderId': order_id},
                UpdateExpression='SET #status = :confirmed',
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':confirmed': 'confirmed'
                }
            )
            
            print(f"Successfully confirmed order: {order_id}")
            records_processed += 1
            
        except Exception as e:
            print(f"Error processing record: {str(e)}")
            print(f"Record: {record}")
            records_failed += 1
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'processed': records_processed,
            'failed': records_failed
        })
    }

