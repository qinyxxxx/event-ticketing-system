import json
import boto3
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')
events_table = dynamodb.Table(os.environ['EVENTS_TABLE'])
orders_table = dynamodb.Table(os.environ['ORDERS_TABLE'])
queue_url = os.environ['QUEUE_URL']

def lambda_handler(event, context):
    try:
        # Parse body: userId, eventId, quantity
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('userId', '')
        event_id = body.get('eventId', '')
        
        try:
            quantity = int(body.get('quantity', 0))
        except (ValueError, TypeError):
            quantity = 0
        
        if not user_id or not event_id or quantity <= 0:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "success": False,
                    "error": "userId, eventId, and quantity (positive) are required"
                })
            }
        
        # DynamoDB conditional update: remainingTickets >= quantity
        try:
            response = events_table.update_item(
                Key={'eventId': event_id},
                UpdateExpression='SET remainingTickets = remainingTickets - :qty',
                ConditionExpression='remainingTickets >= :qty',
                ExpressionAttributeValues={
                    ':qty': quantity
                },
                ReturnValues='UPDATED_NEW'
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return {
                    "statusCode": 400,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps({
                        "success": False,
                        "error": "Not enough tickets available"
                    })
                }
            raise
        
        order_id = f"o{uuid.uuid4().hex[:8]}"
        order_item = {
            'orderId': order_id,
            'userId': user_id,
            'eventId': event_id,
            'quantity': quantity,
            'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'status': 'pending'
        }
        
        # Convert to DynamoDB format (numbers as Decimal)
        dynamodb_item = json.loads(json.dumps(order_item), parse_float=Decimal)
        orders_table.put_item(Item=dynamodb_item)
        
        # Send SQS message (order created)
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps({
                'orderId': order_id,
                'userId': user_id,
                'eventId': event_id,
                'quantity': quantity,
                'createdAt': order_item['createdAt']
            })
        )
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
            },
            "body": json.dumps({
                "success": True,
                "data": {
                    "orderId": order_id,
                    "message": "Purchase successful"
                }
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": False,
                "error": str(e)
            })
        }