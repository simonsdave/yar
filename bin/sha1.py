#!/usr/bin/env python

import sys
import hashlib

if __name__ == "__main__":
	sha1 = hashlib.sha1(sys.stdin.read())
	print sha1.hexdigest()

#------------------------------------------------------------------- End-of-File
