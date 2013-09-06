#!/usr/bin/env python

import sys

import radon.raw

for source_file_name in sys.argv[1:]:
    with open(source_file_name, 'r') as f:
        source_code = f.read()
        print "%s: %d" % (source_file_name, len(source_code))
        scm = radon.raw.analyze(source_code)
        print scm
        print scm.lloc
