#!/usr/bin/env python3

import aws_cdk as cdk
import json

from ec2_example.ec2_example_stack import CdkEc2Stack

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

app = cdk.App()
CdkEc2Stack(app, "CdkEc2Stack",
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    #env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    env=cdk.Environment(account='159168350739', region=config['region']),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    )

app.synth()
