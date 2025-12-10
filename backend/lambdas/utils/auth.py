def verify_token(event):
    """
    Extract and validate Authorization token from Lambda event headers.
    Token format:  token-<userId>
    Returns: userId (string)
    Raises: Exception("Unauthorized") if invalid
    """
    headers = event.get("headers", {}) or {}
    token = headers.get("Authorization", "")

    if not token or not token.startswith("token-"):
        raise Exception("Unauthorized")

    user_id = token.replace("token-", "")
    return user_id


def auth_response_401():
    """Reusable 401 response."""
    return {
        "statusCode": 401,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
        },
        "body": '{"success": false, "error": "Unauthorized"}'
    }