#!/bin/bash

set -ex

cd /work

BUCKET="${1}"

while read -r src dst ; do
    bn=$(basename "${src}")
    echo "Downloading ${bn}..."
    wget --quiet "${src}"
    echo "  Uploading ${bn}..."
    aws --profile secondary s3 cp --quiet "${bn}" "s3://${BUCKET}/${dst}"
    rm -f "${bn}"
done < *.manifest
