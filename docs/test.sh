#!/bin/bash

grep genome-idx k2.md | grep https | awk '{print $2}' > urls.txt

for i in `cat urls.txt` ; do
    curl -I "${i}" 2>&1 | grep -q '200 OK'
    if (( $? != 0 )) ; then
        echo "Could not access URL ${i}"
        exit 1
    fi
done
