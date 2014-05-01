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

cd $SCRIPT_DIR_NAME

cleanup_yar_dist
rm -rf yar/artifacts >& /dev/null
mkdir -p yar/artifacts
build_yar_dist
cp ../dist/yar-*.*.tar.gz yar/artifacts/.
cleanup_yar_dist

rm -rf artifacts >& /dev/null
mkdir -p artifacts
cp ../bin/jpp artifacts/.
cp ../bin/yarcurl artifacts/.

vagrant up
