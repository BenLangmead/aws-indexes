import aws_cdk as core
import aws_cdk.assertions as assertions

from ec2_example.ec2_example_stack import Ec2ExampleStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ec2_example/ec2_example_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = Ec2ExampleStack(app, "ec2-example")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
