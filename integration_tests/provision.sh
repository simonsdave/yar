#!/usr/bin/env bash

cleanup_yar_dist() {
    pushd ..
    rm -rf build >& /dev/null
    rm -rf yar.egg-info >& /dev/null
    rm -rf dist >& /dev/null
    popd
}

build_yar_dist() {
    pushd ..
    python setup.py sdist
    popd
}

if [ $# != 0 ]; then
    echo "usage: `basename $0`"
    exit 1
fi

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

if [ "$PWD" != "$SCRIPT_DIR_NAME" ]; then
    cd $SCRIPT_DIR_NAME
fi

cleanup_yar_dist
rm -rf yar/artifacts >& /dev/null
mkdir yar/artifacts
build_yar_dist
cp ../dist/yar-*.*.tar.gz yar/artifacts/.
cleanup_yar_dist

rm -rf artifacts >& /dev/null
mkdir artifacts
cp ../bin/jpp artifacts/.
cp ../bin/yarcurl artifacts/.

vagrant up
