#!/bin/bash

set -ex

if [ ! -d /work ] ; then
    dv=$(lsblk --output NAME,SIZE | awk "\$2 == \"${VOLUME_GB}G\"" | cut -f1 -d' ')
    mkfs -q -t ext4 /dev/${dv}
    mkdir /work
    mount /dev/${dv} /work/
    chmod a+w /work
fi
