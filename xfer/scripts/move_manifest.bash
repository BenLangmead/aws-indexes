#!/bin/bash

set -ex

mkdir -p /work
mv /tmp/*.manifest /work/
chmod a+r /work/*.manifest
