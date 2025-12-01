import json
import uuid

def lambda_handler(event, context):
    try:
        # Read user info from body
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('userId', '')
        
        # For demo purposes, skip real registration, just return success
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
                    "message": "User created"
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