#!/bin/bash

prof=$(grep '"default_profile":' profile.json | sed 's/[",]//g' | awk '{print $2}')
prof2=$(grep '"secondary_profile":' profile.json | sed 's/[",]//g' | awk '{print $2}')

test -z "${prof}" && echo "Could not parse default profile from profile.json" && exit 1

rm -rf ".${1}" \
  && ./vagrant_run.py "${prof}" "${1}" "${2}" ".${1}" --second-profile="${prof2}"
