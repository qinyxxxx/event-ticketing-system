import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigw,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_event_sources,
)
from constructs import Construct


class TicketingStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # ============================================================
        # 1. DynamoDB Tables
        # ============================================================
        # EventsTable Schema:
        # - eventId (String, PK)
        # - name (String)
        # - description (String)
        # - imageUrl (String)
        # - remainingTickets (Number)
        # ============================================================
        events_table = dynamodb.Table(
            self, "EventsTable",
            partition_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        # ============================================================
        # OrdersTable Schema:
        # - orderId (String, PK)
        # - userId (String) - used in GSI
        # - eventId (String)
        # - quantity (Number)
        # - status (String) - pending/confirmed
        # - createdAt (String) - ISO timestamp
        #
        # GSI: UserOrdersIndex
        # - userId (String, PK)
        # - createdAt (String, SK) - for sorting by time
        # ============================================================
        orders_table = dynamodb.Table(
            self, "OrdersTable",
            partition_key=dynamodb.Attribute(
                name="orderId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )
        
        # Add GSI for querying orders by userId
        orders_table.add_global_secondary_index(
            index_name="UserOrdersIndex",
            partition_key=dynamodb.Attribute(
                name="userId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt",
                type=dynamodb.AttributeType.STRING
            )
        )

        # ============================================================
        # 2. SQS (OrderCreated Queue)
        # ============================================================
        # Dead Letter Queue for failed order processing
        # Messages that fail processing after maxReceiveCount will be sent here
        # ============================================================
        order_dlq = sqs.Queue(
            self, "OrderCreatedDLQ",
            # Keep failed messages for 14 days
            retention_period=cdk.Duration.days(14)
        )

        order_queue = sqs.Queue(
            self, "OrderCreatedQueue",
            visibility_timeout=cdk.Duration.seconds(30),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,  # Retry 3 times before sending to DLQ
                queue=order_dlq
            )
        )

        order_consumer_lambda = _lambda.Function(
            self,
            "order-consumer-lambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="order_consumer.lambda_handler",
            code=_lambda.Code.from_asset("../lambdas"),
            timeout=cdk.Duration.seconds(30),
            environment={
                "ORDERS_TABLE": orders_table.table_name
            }
        )

        orders_table.grant_read_write_data(order_consumer_lambda)
        order_queue.grant_consume_messages(order_consumer_lambda)

        order_consumer_lambda.add_event_source(
            lambda_event_sources.SqsEventSource(
                order_queue,
                batch_size=10
            )
        )

        # ============================================================
        # 3. Create Lambdas
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
            events_table.grant_read_write_data(fn)
            orders_table.grant_read_write_data(fn)
            order_queue.grant_send_messages(fn)

        # ============================================================
        # 4. API Gateway structure
        # ============================================================
        api = apigw.RestApi(
            self,
            "TicketingAPI",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=["*"],
                allow_methods=["GET", "POST", "OPTIONS"],
                allow_headers=["Content-Type", "Authorization"]
            )
        )

        cors_response = apigw.MethodResponse(
            status_code="200",
            response_parameters={
                "method.response.header.Access-Control-Allow-Origin": True
            }
        )

        register_resource = api.root.add_resource("register")
        register_resource.add_method(
            "POST",
            apigw.LambdaIntegration(lambda_functions["register"]),
            method_responses=[cors_response]
        )

        login_resource = api.root.add_resource("login")
        login_resource.add_method(
            "POST",
            apigw.LambdaIntegration(lambda_functions["login"]),
            method_responses=[cors_response]
        )

        events_resource = api.root.add_resource("events")
        events_resource.add_method(
            "GET",
            apigw.LambdaIntegration(lambda_functions["get_events"]),
            method_responses=[cors_response]
        )

        event_detail_resource = events_resource.add_resource("{eventId}")
        event_detail_resource.add_method(
            "GET",
            apigw.LambdaIntegration(lambda_functions["get_event_detail"]),
            method_responses=[cors_response]
        )

        purchase_resource = api.root.add_resource("purchase")
        purchase_resource.add_method(
            "POST",
            apigw.LambdaIntegration(lambda_functions["purchase"]),
            method_responses=[cors_response]
        )

        orders_resource = api.root.add_resource("orders")
        orders_resource.add_method(
            "GET",
            apigw.LambdaIntegration(lambda_functions["get_orders"]),
            method_responses=[cors_response]
        )

        order_detail_resource = orders_resource.add_resource("{orderId}")
        order_detail_resource.add_method(
            "GET",
            apigw.LambdaIntegration(lambda_functions["get_order_detail"]),
            method_responses=[cors_response]
        )

        # ============================================================
        # 5. (Optional) CloudWatch alarms, logging, metrics
        # TODO
        # ============================================================
