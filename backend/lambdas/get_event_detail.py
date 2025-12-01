import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
events_table = dynamodb.Table(os.environ['EVENTS_TABLE'])

def lambda_handler(event, context):
    try:
        # Read eventId from pathParameters
        event_id = event.get('pathParameters', {}).get('eventId')
        
        if not event_id:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "success": False,
                    "error": "eventId is required"
                })
            }
        
        # Get item from EventsTable
        response = events_table.get_item(Key={'eventId': event_id})
        
        if 'Item' not in response:
            return {
                "statusCode": 404,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "success": False,
                    "error": "Event not found"
                })
            }
        
        item = response['Item']
        event_detail = {
            'eventId': item.get('eventId'),
            'name': item.get('name', ''),
            'description': item.get('description', ''),
            'imageUrl': item.get('imageUrl', ''),
            'remainingTickets': int(item.get('remainingTickets', 0)) if 'remainingTickets' in item else 0
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
                "data": event_detail
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