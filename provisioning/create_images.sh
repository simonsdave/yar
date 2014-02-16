#!/usr/bin/env bash

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

cd $SCRIPT_DIR_NAME

pushd Key-Store
sudo docker build -t key_store_img .
popd

exit 0

pushd yar
sudo docker build -t yar_img .
popd

pushd Nonce-Store
sudo docker build -t key_store_img .
popd

exit 0
