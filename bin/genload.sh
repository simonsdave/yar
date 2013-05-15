#!/bin/bash

if [ $# != 0 ]; then
	echo "usage: `basename $0`"
	exit 1
fi

for bp in {1..25};
do
	for i in {1..100}; do echo $i; hcurl.sh GET /dave/was/here-$bp-$i.html; done &
done

wait
echo "done"

exit 0

#------------------------------------------------------------------- End-of-File
