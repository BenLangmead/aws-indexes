#!/bin/bash

ssh -i movi-mem-bench.pem -o "IdentitiesOnly yes" \
    ec2-user@$(cat outputs.json | tr -d "\",:" | awk '$1 == "PublicIp" {print $2}')
