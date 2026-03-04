#!/bin/bash

set -ex

if [ "$1" != "skip" ]; then
    npx aws-cdk bootstrap
    npx aws-cdk synth
    npx aws-cdk deploy --outputs-file outputs.json --require-approval never
fi

region=$(cat config.json | tr -d '",:' | awk '$1 == "region" {print $2}')
key_name=$(cat outputs.json | tr -d '",:' | awk '$1 == "KeyPairId" {print $2}')

# Get private key so we can SSH
aws ssm get-parameter \
    --region ${region} \
    --name /ec2/keypair/${key_name} \
    --with-decryption \
    --query Parameter.Value \
    --output text > tera-build.pem

chmod 600 tera-build.pem
