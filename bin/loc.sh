#!/bin/bash

if [ $# != 0 ]; then
    echo "usage: `basename $0`"
    exit 1
fi

cat `ls *.py | grep -v _unit_tests\.py | grep -v testcase\.py` | grep -v "^\\s*$" | grep -v "^#" | wc -l

exit 0
