#!/bin/bash
# This super simple bash script computes the number of lines of
# code (LOC) for each python source file in the current directory.
# LOC is determined by taking all of the source code (not test code),
# eliminating blank lines, comments and asserts. The LOC is then
# computed by taking counting number of lines of code of this
# modified source.

if [ $# != 0 ]; then
    echo "usage: `basename $0`"
    exit 1
fi

cat `ls *.py | \
	grep -v _unit_tests\.py | \
	grep -v testcase\.py` | \
	grep -v "^\\s*$" | \
	grep -v "^#" | \
	grep -v "^\s*assert.*" | \
	wc -l

exit 0
