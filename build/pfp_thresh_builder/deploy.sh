#!/bin/bash

set -ex

if [ "$1" != "skip" ]; then
    cdk bootstrap
    cdk synth
    cdk deploy --outputs-file outputs.json --require-approval never
fi

region=$(cat config.json | tr -d "\",:" | awk '$1 == "region" {print $2}')
key_name=$(cat outputs.json | tr -d "\",:" | awk '$1 == "KeyPairId" {print $2}')

# Get private key so we can SSH
aws ssm get-parameter \
    --region ${region} \
    --name /ec2/keypair/${key_name} \
    --with-decryption \
    --query Parameter.Value \
    --output text > hprc-build.pem
