#!/usr/bin/env bash

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

sudo docker build -t yar_img $SCRIPT_DIR_NAME/yar

exit 0
