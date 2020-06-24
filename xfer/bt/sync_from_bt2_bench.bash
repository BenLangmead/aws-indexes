#!/bin/bash

set -ex

cd /work

SOURCE="${1}"
DEST="${2}"

for i in $(aws s3 ls "s3://${SOURCE}" | awk '{print $NF}') ; do
    echo "Downloading ${i}..."
    aws s3 cp "s3://${SOURCE}/${i}" .
    echo "  Uploading ${i}..."
    aws --profile secondary s3 cp "${i}" "S3://${DEST}/${i}"
    rm -f "${i}"
done
