#!/usr/bin/env bash

if [ $# != 0 ]; then
    echo "usage: `basename $0`"
    exit 1
fi

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

if [ "$PWD" != "$SCRIPT_DIR_NAME" ]; then
    cd $SCRIPT_DIR_NAME
fi

rm yar/yar-*.*.tar.gz

pushd ..
rm -rf build >& /dev/null
rm -rf clf.egg-info >& /dev/null
rm -rf dist >& /dev/null
python setup.py sdist
popd
cp ../dist/yar-*.*.tar.gz yar/.

vagrant up
