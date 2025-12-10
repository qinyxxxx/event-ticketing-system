import json
from datetime import datetime

import boto3
import os

from decimal import Decimal
from utils.auth import verify_token, auth_response_401


def _normalize_decimals(value):
    """Recursively convert DynamoDB Decimals into int/float for JSON serialization."""
    if isinstance(value, list):
        return [_normalize_decimals(v) for v in value]
    if isinstance(value, dict):
        return {k: _normalize_decimals(v) for k, v in value.items()}
    if isinstance(value, Decimal):
        # If it's an integer-like decimal, cast to int, otherwise to float
        return int(value) if value % 1 == 0 else float(value)
    return value

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table(os.environ['ORDERS_TABLE'])
events_table = dynamodb.Table(os.environ['EVENTS_TABLE'])


def lambda_handler(event, context):
    try:
        # Authenticate user from token
        try:
            user_id = verify_token(event)
        except:
            return auth_response_401()

        # Query orders by userId using GSI (UserOrdersIndex)
        # GSI: partition key = userId, sort key = createdAt
        response = orders_table.query(
            IndexName='UserOrdersIndex',
            KeyConditionExpression='userId = :uid',
            ExpressionAttributeValues={':uid': user_id},
            # Sort descending by createdAt (newest first)
            ScanIndexForward=False
        )

        orders = response.get('Items', [])

        # Format orders for API response
        formatted_orders = []
        for item in orders:
            event_id = item.get('eventId')
            quantity = int(item.get('quantity', 0)) if 'quantity' in item else 0
            raw_created_at = item.get('createdAt', '')
            formatted_created_at = raw_created_at
            try:
                dt = datetime.fromisoformat(raw_created_at.replace('Z', '+00:00'))
                formatted_created_at = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
            raw_event_item = events_table.get_item(Key={'eventId': event_id}).get('Item', {})
            event_item = _normalize_decimals(raw_event_item)

            formatted_orders.append({
                'orderId': item.get('orderId'),
                'eventId': event_id,
                'quantity': quantity,
                'createdAt': formatted_created_at,
                'event': event_item
            })

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
                "data": formatted_orders
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
