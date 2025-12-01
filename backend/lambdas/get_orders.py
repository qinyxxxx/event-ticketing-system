import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table(os.environ['ORDERS_TABLE'])

def lambda_handler(event, context):
    try:
        # Read userId from query parameters
        query_params = event.get('queryStringParameters') or {}
        user_id = query_params.get('userId', '')
        
        if not user_id:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "success": False,
                    "error": "userId query parameter is required"
                })
            }
        
        # Scan and filter by userId (for demo - in production use GSI)
        response = orders_table.scan(
            FilterExpression='userId = :uid',
            ExpressionAttributeValues={':uid': user_id}
        )
        
        orders = response.get('Items', [])
        
        # Format orders for API response
        formatted_orders = []
        for item in orders:
            formatted_orders.append({
                'orderId': item.get('orderId'),
                'eventId': item.get('eventId'),
                'quantity': int(item.get('quantity', 0)) if 'quantity' in item else 0
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