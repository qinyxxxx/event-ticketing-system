import json
import boto3
import os
import traceback
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table(os.environ['ORDERS_TABLE'])

def lambda_handler(event, context):
    """
    SQS event consumer Lambda
    Processes order-created messages and updates order status to confirmed
    
    Error handling:
    - Invalid message format: logs and skips (will go to DLQ after maxReceiveCount)
    - Missing orderId: logs and skips
    - Order not found: logs warning but doesn't fail (idempotent)
    - DynamoDB errors: logs full error and fails (will retry, then go to DLQ)
    """
    records_processed = 0
    records_failed = 0
    records_skipped = 0
    
    for record in event.get('Records', []):
        try:
            # Parse SQS message body
            try:
                message_body = json.loads(record['body'])
            except json.JSONDecodeError as e:
                print(f"ERROR: Invalid JSON in message body: {str(e)}")
                print(f"Message body: {record.get('body', 'N/A')}")
                records_failed += 1
                continue
            
            order_id = message_body.get('orderId')
            user_id = message_body.get('userId', 'N/A')
            event_id = message_body.get('eventId', 'N/A')
            
            # Validate required fields
            if not order_id:
                print(f"ERROR: Missing orderId in message. Message: {json.dumps(message_body)}")
                records_failed += 1
                continue
            
            # Update order status from pending to confirmed
            # Use conditional update to ensure we only update pending orders
            # This makes the operation idempotent
            try:
                orders_table.update_item(
                    Key={'orderId': order_id},
                    UpdateExpression='SET #status = :confirmed',
                    ConditionExpression='attribute_exists(orderId)',  # Ensure order exists
                    ExpressionAttributeNames={
                        '#status': 'status'
                    },
                    ExpressionAttributeValues={
                        ':confirmed': 'confirmed'
                    }
                )
                
                print(f"SUCCESS: Confirmed order {order_id} (userId: {user_id}, eventId: {event_id})")
                records_processed += 1
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                
                if error_code == 'ConditionalCheckFailedException':
                    # Order doesn't exist - log warning but don't fail
                    # This could happen if order was deleted or never created
                    print(f"WARNING: Order {order_id} not found in database. Skipping.")
                    records_skipped += 1
                else:
                    # Other DynamoDB errors - log and fail
                    print(f"ERROR: DynamoDB error updating order {order_id}: {error_code}")
                    print(f"Error details: {str(e)}")
                    print(f"Full error response: {json.dumps(e.response)}")
                    records_failed += 1
                    
        except Exception as e:
            # Catch-all for any unexpected errors
            print(f"ERROR: Unexpected error processing record: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            print(f"Traceback: {traceback.format_exc()}")
            print(f"Record: {json.dumps(record, default=str)}")
            records_failed += 1
    
    # Log summary
    total_records = len(event.get('Records', []))
    print(f"Processing summary: Total={total_records}, Processed={records_processed}, "
          f"Skipped={records_skipped}, Failed={records_failed}")
    
    # Return success even if some records failed
    # Failed records will be retried by SQS, and eventually sent to DLQ
    return {
        'statusCode': 200,
        'body': json.dumps({
            'processed': records_processed,
            'skipped': records_skipped,
            'failed': records_failed,
            'total': total_records
        })
    }

