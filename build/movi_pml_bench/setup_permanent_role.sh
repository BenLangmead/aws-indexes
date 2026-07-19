#!/usr/bin/env bash
#
# ONE-TIME setup of the PERMANENT instance role used by the movi_kmer_bench CDK
# stack. Run this once (it is idempotent). After this, `cdk deploy`/`cdk destroy`
# no longer create or delete the role, so the cross-account trust on
# S3UploadFromComputeRole (account 128342663110) is set once and never breaks.
#
# Account: 159168350739 (jhu-langmead). Requires a fresh SSO session:
#     aws sso login --profile jhu-langmead
#
# What it creates:
#   - IAM role index-zone-movi-kmer-bench-role  (trusts ec2.amazonaws.com)
#   - inline policy  assume-upload-role  (sts:AssumeRole on the upload role)
#
# It does NOT create an instance profile: the CDK LaunchTemplate creates an
# ephemeral one wrapping this role on each deploy (harmless -- instance profiles
# are never named in trust policies).
#
# After running this, do the matching ONE-TIME trust edit in 128342663110 (see
# README.md "Permanent role" section): make S3UploadFromComputeRole trust
#   arn:aws:iam::159168350739:role/index-zone-movi-kmer-bench-role
set -euo pipefail

PROFILE="${PROFILE:-jhu-langmead}"
ROLE_NAME="${ROLE_NAME:-index-zone-movi-kmer-bench-role}"
UPLOAD_ROLE_ARN="${UPLOAD_ROLE_ARN:-arn:aws:iam::128342663110:role/S3UploadFromComputeRole}"

echo ">> using profile=$PROFILE role=$ROLE_NAME"
aws --profile "$PROFILE" sts get-caller-identity

TRUST_DOC='{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}
  ]
}'

POLICY_DOC="{
  \"Version\": \"2012-10-17\",
  \"Statement\": [
    {\"Effect\": \"Allow\", \"Action\": \"sts:AssumeRole\", \"Resource\": \"${UPLOAD_ROLE_ARN}\"}
  ]
}"

if aws --profile "$PROFILE" iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
  echo ">> role exists; ensuring trust + inline policy are current"
  aws --profile "$PROFILE" iam update-assume-role-policy \
      --role-name "$ROLE_NAME" --policy-document "$TRUST_DOC"
else
  echo ">> creating role"
  aws --profile "$PROFILE" iam create-role \
      --role-name "$ROLE_NAME" \
      --assume-role-policy-document "$TRUST_DOC" \
      --description "Permanent EC2 instance role for movi_kmer_bench (referenced, not created, by CDK)"
fi

aws --profile "$PROFILE" iam put-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-name assume-upload-role \
    --policy-document "$POLICY_DOC"

ROLE_ARN=$(aws --profile "$PROFILE" iam get-role --role-name "$ROLE_NAME" \
             --query 'Role.Arn' --output text)
echo
echo ">> DONE. Permanent instance role ARN:"
echo "   $ROLE_ARN"
echo
echo ">> NEXT (one-time, account 128342663110): make S3UploadFromComputeRole trust"
echo "   the ARN above. See README.md 'Permanent role' section for the trust JSON."
