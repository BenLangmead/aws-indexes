#!/usr/bin/env python3

import json
import aws_cdk as cdk

from movi_index_build_stack.movi_index_build_stack import MoviIndexBuildStack

with open('config.json', 'r') as f:
    config = json.load(f)

_profile = config["instance_profile"]
if _profile not in config.get("instance_type", {}):
    raise ValueError(
        f'config.json: instance_profile {_profile!r} not found under instance_type'
    )
_region = config["instance_type"][_profile]["region"]

app = cdk.App()
MoviIndexBuildStack(
    app, "MoviIndexBuildStack",
    env=cdk.Environment(account='159168350739', region=_region),
)
app.synth()
