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
        formatted_events = []  # list to collect normalized event records
        for item in events:
            formatted_events.append({
                'eventId': item.get('eventId'),
                'name': item.get('name', ''),
                'description': item.get('description', ''),
                'imageUrl': item.get('imageUrl', ''),
                'remainingTickets': int(item.get('remainingTickets', 0)) if 'remainingTickets' in item else 0,
                'performer': item.get('performer', ''),
                'venue': item.get('venue', ''),
                'city': item.get('city', ''),
                'date': item.get('date', ''),
                'price': float(item.get('price', 0)) if 'price' in item else 0,
                'category': item.get('category', '')
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