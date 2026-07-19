#!/bin/bash
# Tear down the stack (ASG, VPC, key pair). Does NOT delete S3 checkpoints/output.
export JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1
export NODE_OPTIONS="${NODE_OPTIONS:+$NODE_OPTIONS }--no-deprecation"
npx aws-cdk destroy --force
