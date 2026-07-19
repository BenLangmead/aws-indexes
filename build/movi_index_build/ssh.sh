#!/bin/bash
# Find the (single) ASG-managed instance's public IP and SSH in.
set -e

region=$(python3 -c "import json; c=json.load(open('config.json')); p=c['instance_profile']; print(c['instance_type'][p]['region'])")
asg=$(python3 -c "import json; print(json.load(open('config.json'))['asg_name'])")
key_name=$(python3 -c "import json; print(json.load(open('config.json'))['key_name'])")

ip=$(aws ec2 describe-instances \
    --region "$region" \
    --filters "Name=tag:aws:autoscaling:groupName,Values=${asg}" \
              "Name=instance-state-name,Values=running" \
    --query 'Reservations[].Instances[].PublicIpAddress' \
    --output text | head -1)

if [ -z "$ip" ] || [ "$ip" = "None" ]; then
    echo "No running instance found for ASG ${asg} in ${region} (still launching, or scaled to 0?)." >&2
    exit 1
fi

echo "Connecting to ${ip} ... (job log: tail -f /data/job.out ; cloud-init: /var/log/cloud-init-output.log)"
ssh -i "${key_name}.pem" -o "IdentitiesOnly yes" -o "StrictHostKeyChecking accept-new" ec2-user@"${ip}"
