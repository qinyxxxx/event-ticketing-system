import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigw,
    aws_sqs as sqs,
)
from constructs import Construct


class TicketingStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # ============================================================
        # 1. DynamoDB Tables
        # ============================================================
        # TODO (Bo)
        # - Define the exact schema (attributes, types)
        # - Add GSIs if needed (for user orders, etc.)
        # - Preload seed events after deployment (optional)
        # ============================================================
        events_table = dynamodb.Table(
            self, "EventsTable",
            partition_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            )
        )

        orders_table = dynamodb.Table(
            self, "OrdersTable",
            partition_key=dynamodb.Attribute(
                name="orderId",
                type=dynamodb.AttributeType.STRING
            )
        )

        # ============================================================
        # 2. SQS (OrderCreated Queue)
        # ============================================================
        # TODO (Bo)
        # - Create a consumer Lambda to process order-created events
        # - Write SQS → Lambda integration
        # ============================================================
        order_queue = sqs.Queue(
            self, "OrderCreatedQueue",
            visibility_timeout=cdk.Duration.seconds(30)
        )

        # ============================================================
        # 3. Create Lambdas (Handlers are empty — business needed)
        # ============================================================
        lambda_functions = {}
        lambda_names = [
            "register",
            "login",
            "get_events",
            "get_event_detail",
            "purchase",
            "get_orders",
            "get_order_detail"
        ]

        for name in lambda_names:
            fn = _lambda.Function(
                self,
                f"{name}-lambda",
                runtime=_lambda.Runtime.PYTHON_3_11,
                handler=f"{name}.lambda_handler",
                code=_lambda.Code.from_asset("../lambdas"),
                timeout=cdk.Duration.seconds(10),
                environment={
                    "EVENTS_TABLE": events_table.table_name,
                    "ORDERS_TABLE": orders_table.table_name,
                    "QUEUE_URL": order_queue.queue_url
                }
            )

            lambda_functions[name] = fn

            # TODO
            # Each handler must write its business logic
            events_table.grant_read_write_data(fn)
            orders_table.grant_read_write_data(fn)
            order_queue.grant_send_messages(fn)

        # ============================================================
        # 4. API Gateway structure
        # ============================================================
        # TODO (Eileen: API Gateway)
        # - Add CORS if needed
        # - Add request validation if needed
        # - Add auth (if later required)
        # ============================================================
        api = apigw.RestApi(self, "TicketingAPI")

        # /register
        api.root.add_resource("register").add_method(
            "POST", apigw.LambdaIntegration(lambda_functions["register"])
        )

        # /login
        api.root.add_resource("login").add_method(
            "POST", apigw.LambdaIntegration(lambda_functions["login"])
        )

        # /events
        events = api.root.add_resource("events")
        events.add_method(
            "GET",
            apigw.LambdaIntegration(lambda_functions["get_events"])
        )

        # /events/{eventId}
        event_detail = events.add_resource("{eventId}")
        event_detail.add_method(
            "GET",
            apigw.LambdaIntegration(lambda_functions["get_event_detail"])
        )

        # /purchase
        api.root.add_resource("purchase").add_method(
            "POST",
            apigw.LambdaIntegration(lambda_functions["purchase"])
        )

        # /orders
        orders = api.root.add_resource("orders")
        orders.add_method(
            "GET",
            apigw.LambdaIntegration(lambda_functions["get_orders"])
        )

        # /orders/{orderId}
        order_detail = orders.add_resource("{orderId}")
        order_detail.add_method(
            "GET",
            apigw.LambdaIntegration(lambda_functions["get_order_detail"])
        )

        # ============================================================
        # 5. (Optional) CloudWatch alarms, logging, metrics
        # TODO
        # ============================================================