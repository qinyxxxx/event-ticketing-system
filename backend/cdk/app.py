from aws_cdk import App, Environment
from ticketing_stack import TicketingStack
from frontend_stack import FrontendStack

app = App()

env = Environment(
    account="455896786481", # 直接用我的account id，不需要改
    region="us-east-1"
)

TicketingStack(app, "TicketingStack", env=env)
FrontendStack(app, "FrontendStack", env=env)

app.synth()