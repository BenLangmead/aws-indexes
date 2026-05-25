#!/usr/bin/env python3

import json

import aws_cdk as cdk

from bowtie_stack.bowtie_stack import BowtieStack


with open("config.json", "r") as f:
    config = json.load(f)

profile = config["instance_profile"]
if profile not in config.get("instance_type", {}):
    raise ValueError(
        f"config.json: instance_profile {profile!r} not found under instance_type"
    )

region = config["instance_type"][profile]["region"]
account = config.get("account", "159168350739")

app = cdk.App()
BowtieStack(
    app,
    "BowtieStack",
    env=cdk.Environment(account=account, region=region),
)

app.synth()
