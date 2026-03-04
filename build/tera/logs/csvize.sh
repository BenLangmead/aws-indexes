#!/bin/bash

grep seconds ${1} | sed 's/.*Ending //' | sed 's/\. It took /,/' | sed 's/ seconds//' | sed 's/, seqLens,/ seqLens/'
