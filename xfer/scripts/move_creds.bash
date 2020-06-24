#!/bin/bash

set -ex

mkdir ~/.aws
mv /tmp/credentials ~/.aws/
chmod go-rwx ~/.aws/credentials
