import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table(os.environ['ORDERS_TABLE'])


def lambda_handler(event, context):
    try:
        # Read orderId from pathParameters
        order_id = event.get('pathParameters', {}).get('orderId')

        if not order_id:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "success": False,
                    "error": "orderId is required"
                })
            }

        # Get item from OrdersTable
        response = orders_table.get_item(Key={'orderId': order_id})

        if 'Item' not in response:
            return {
                "statusCode": 404,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "success": False,
                    "error": "Order not found"
                })
            }

        item = response['Item']
        raw_created_at = item.get('createdAt', '')
        formatted_created_at = raw_created_at
        try:
            dt = datetime.fromisoformat(raw_created_at.replace('Z', '+00:00'))
            formatted_created_at = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
        order_detail = {
            'orderId': item.get('orderId'),
            'eventId': item.get('eventId'),
            'quantity': int(item.get('quantity', 0)) if 'quantity' in item else 0,
            'status': item.get('status', 'unknown'),
            'userId': item.get('userId', ''),
            'createdAt': formatted_created_at
        }

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
                "data": order_detail
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
