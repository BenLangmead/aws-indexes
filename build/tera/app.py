#!/usr/bin/env python3

import aws_cdk as cdk
import json

from tera_stack.tera_stack import TeraStack

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

app = cdk.App()
TeraStack(app, "TeraStack",
    env=cdk.Environment(account='159168350739', region=config['region']),
    )

app.synth()
