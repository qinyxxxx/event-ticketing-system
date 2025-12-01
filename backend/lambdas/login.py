import json
import uuid

def lambda_handler(event, context):
    try:
        # Parse body userId/password
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('userId', '')
        
        token = f"mock-token-{user_id}"
        
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
                    "token": token,
                    "userId": user_id
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