#!/bin/bash
# Silence JSII untested Node version warning and Node deprecation warnings (e.g. url.parse)
export JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1
export NODE_OPTIONS="${NODE_OPTIONS:+$NODE_OPTIONS }--no-deprecation"
npx aws-cdk destroy --force
