import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
events_table = dynamodb.Table(os.environ['EVENTS_TABLE'])

def lambda_handler(event, context):
    try:
        # Scan EventsTable to get all events
        response = events_table.scan()
        events = response.get('Items', [])
        
        # Transform DynamoDB items into API output format
        # DynamoDB returns numbers as Decimal, convert to int
        formatted_events = []
        for item in events:
            formatted_events.append({
                'eventId': item.get('eventId'),
                'name': item.get('name', ''),
                'description': item.get('description', ''),
                'imageUrl': item.get('imageUrl', ''),
                'remainingTickets': int(item.get('remainingTickets', 0)) if 'remainingTickets' in item else 0
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
                "data": formatted_events
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