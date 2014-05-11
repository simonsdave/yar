#!/usr/bin/env bash

if [ $# != 0 ]; then
    echo "usage: `basename $0`"
    exit 1
fi

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

cleanup_yar_dist() {
    pushd "$SCRIPT_DIR_NAME/.."
    rm -rf build >& /dev/null
    rm -rf yar.egg-info >& /dev/null
    rm -rf dist >& /dev/null
    popd
}

cleanup_yar_dist

pushd "$SCRIPT_DIR_NAME/.."
python setup.py sdist --formats=gztar
if ! cp "$(pwd)/dist/yar-1.0.tar.gz" "$SCRIPT_DIR_NAME/."; then
    exit 2
fi
popd

cleanup_yar_dist

vagrant up
