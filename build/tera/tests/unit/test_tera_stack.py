import aws_cdk as core
import aws_cdk.assertions as assertions

from tera_stack.tera_stack import TeraStack

# example tests. To run these tests, uncomment this file along with the example
# resource in tera_stack/tera_stack.py
def test_ec2_instance_created():
    app = core.App()
    stack = TeraStack(app, "tera")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::EC2::Instance", {
#     })
