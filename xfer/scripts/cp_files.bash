#!/bin/bash

set -ex

cd /work

BUCKET="${1}"

while read -r src dst ; do
    if [[ "${src}" = "#"* ]] ; then continue ; fi
    bn=$(basename "${src}")
    if [[ "${src}" = "s3://"* ]] ; then
        echo "Downloading ${bn} from S3..."
        aws s3 cp --quiet "${src}" "${bn}"
    else
        echo "Downloading ${bn}..."
        wget --quiet "${src}"
    fi
    echo "  Uploading ${bn}..."
    aws --profile secondary s3 cp --quiet "${bn}" "s3://${BUCKET}/${dst}"
    rm -f "${bn}"
done < *.manifest
