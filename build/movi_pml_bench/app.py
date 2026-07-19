#!/usr/bin/env python3

import aws_cdk as cdk
import json

from ec2_example.ec2_example_stack import CdkEc2Stack

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

app = cdk.App()
CdkEc2Stack(app, "MoviPmlBenchStack",
    env=cdk.Environment(account='159168350739', region=config['region']),
    )

app.synth()
