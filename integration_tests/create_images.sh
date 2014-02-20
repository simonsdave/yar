#!/usr/bin/env bash

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

cd $SCRIPT_DIR_NAME

pushd Nonce-Store
sudo docker build -t nonce_store_img .
popd

pushd Key-Store
sudo docker build -t key_store_img .
popd

pushd yar
sudo docker build -t yar_img .
popd

exit 0
