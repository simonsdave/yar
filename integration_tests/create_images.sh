#!/usr/bin/env bash

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

sudo docker build -t auth_server_lb_img $SCRIPT_DIR_NAME/Auth-Server-LB
sudo docker build -t app_server_lb_img $SCRIPT_DIR_NAME/App-Server-LB
sudo docker build -t memcached_img $SCRIPT_DIR_NAME/memcached
sudo docker build -t couchdb_img $SCRIPT_DIR_NAME/CouchDB
sudo docker build -t yar_img $SCRIPT_DIR_NAME/yar

exit 0
