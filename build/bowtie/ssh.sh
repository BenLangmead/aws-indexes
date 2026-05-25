#!/bin/bash

set -euo pipefail

public_ip="$(
    python3 - <<'PY'
import json
import sys

try:
    with open("outputs.json") as f:
        outputs = json.load(f)
except FileNotFoundError:
    print("outputs.json not found; run ./deploy.sh first", file=sys.stderr)
    sys.exit(1)

public_ip = outputs.get("BowtieStack", {}).get("PublicIp")
if not public_ip:
    print(
        "BowtieStack output PublicIp is missing; set launch_instance=true and redeploy first",
        file=sys.stderr,
    )
    sys.exit(1)

print(public_ip)
PY
)"

ssh -i bowtie-build.pem -o "IdentitiesOnly yes" "ec2-user@${public_ip}"
