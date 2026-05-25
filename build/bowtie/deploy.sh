#!/bin/bash

set -ex

if ! python3 -c 'import aws_cdk' 2>/dev/null; then
    echo "Error: Unable to import aws_cdk. Activate the project venv first: source .venv/bin/activate" >&2
    exit 1
fi

export JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1
export NODE_OPTIONS="${NODE_OPTIONS:+$NODE_OPTIONS }--no-deprecation"

cdk_profile_args=()
if [ -n "${AWS_PROFILE:-}" ]; then
    cdk_profile_args=(--profile "${AWS_PROFILE}")
fi

if [ "${1:-}" != "skip" ]; then
    npx aws-cdk bootstrap "${cdk_profile_args[@]}"
    npx aws-cdk synth "${cdk_profile_args[@]}"
    npx aws-cdk deploy "${cdk_profile_args[@]}" --outputs-file outputs.json --require-approval never
fi

region=$(python3 -c "import json; c=json.load(open('config.json')); p=c['instance_profile']; print(c['instance_type'][p]['region'])")
key_name=$(cat outputs.json | tr -d '",:' | awk '$1 == "KeyPairId" {print $2}')

aws ssm get-parameter \
    --region "${region}" \
    --name "/ec2/keypair/${key_name}" \
    --with-decryption \
    --query Parameter.Value \
    --output text > bowtie-build.pem

chmod 600 bowtie-build.pem
