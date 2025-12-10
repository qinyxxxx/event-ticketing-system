import json
import boto3
import os

dynamodb = boto3.resource("dynamodb")
users_table = dynamodb.Table(os.environ["USERS_TABLE"])

def lambda_handler(event, context):
    try:
        # Parse body userId/password
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('userId', '')

        password = body.get("password", "")

        if not user_id or not password:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization",
                    "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
                },
                "body": json.dumps({
                    "success": False,
                    "error": "Missing userId or password"
                })
            }

        user = users_table.get_item(Key={"userId": user_id}).get("Item")

        if not user or user.get("password") != password:
            return {
                "statusCode": 401,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization",
                    "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
                },
                "body": json.dumps({
                    "success": False,
                    "error": "Invalid userId or password"
                })
            }

        token = f"token-{user_id}"

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