#!/usr/bin/env python

import sys
import hashlib

def do_it(content):
	print "content = >>>%s<<<" % content.replace('\n','\\n').replace('\r','\\r').replace('\t','\\t')
	print "length = >>>%d<<<" % len(content)
	sha1 = hashlib.sha1(content)
	print "sha1 hexdigest = >>>%s<<<" % sha1.hexdigest()

if __name__ == "__main__":
	if 1 < len(sys.argv):
		for argv in sys.argv[1:]:
			with open(argv, "r") as file:
				do_it(file.read())
	else:
		do_it(sys.stdin.read())

#------------------------------------------------------------------- End-of-File
