#!/usr/bin/env bash

# sudo docker kill `sudo docker ps -notrunc -a -q`
# sudo docker rm `sudo docker ps -notrunc -a -q`

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

get_container_ip() {
    sudo docker inspect -format '{{ .NetworkSettings.IPAddress }}' ${1:-}
}

create_nonce_store() {
    PORT=11211
    NONCE_STORE_CMD=""
    NONCE_STORE=$(sudo docker run -d nonce_store_img $NONCE_STORE_CMD)
    NONCE_STORE_IP=$(get_container_ip $NONCE_STORE)

    for i in {1..10}
    do
		sleep 1
        if [ "$(memcstat --servers=$NONCE_STORE_IP:$PORT | wc -l)" != "0" ]; then
		    break
	    fi
    done

    echo $NONCE_STORE_IP:$PORT
}

create_key_server() {
    PORT=8070
    KEY_SERVER_CMD="key_server --log=info --lon=$PORT --key_store=${1:-}"
    KEY_SERVER=$(sudo docker run -d yar_img $KEY_SERVER_CMD)
    KEY_SERVER_IP=$(get_container_ip $KEY_SERVER)

    for i in {1..10}
    do
		sleep 1
        curl -s http://$KEY_SERVER_IP:$PORT/v1.0/creds >& /dev/null
	    if [ $? == 0 ]; then
		    break
	    fi
    done

    echo $KEY_SERVER_IP:$PORT
}

create_key_store() {
    PORT=5984
    DATABASE=creds

    KEY_STORE=$(sudo docker run -d key_store_img)
    KEY_STORE_IP=$(get_container_ip $KEY_STORE)

    for i in {1..10}
    do
		sleep 1
        curl -s http://$KEY_SERVER_IP:$PORT >& /dev/null
	    if [ $? == 0 ]; then
		    break
	    fi
    done

    INSTALL_CMD="key_store_installer --log=info --create=true --host=$KEY_STORE_IP:$PORT --database=$DATABASE"
    sudo docker run -i -t yar_img $INSTALL_CMD >& /dev/null

    for i in {1..10}
    do
		sleep 1
        curl -s http://$KEY_STORE_IP:$PORT/$DATABASE >& /dev/null
	    if [ $? == 0 ]; then
		    break
	    fi
    done

    echo $KEY_STORE_IP:$PORT/$DATABASE
}

create_app_server() {
    PORT=8080
    APP_SERVER_CMD="app_server --log=info --lon=$PORT"
    APP_SERVER=$(sudo docker run -d yar_img $APP_SERVER_CMD)
    APP_SERVER_IP=$(get_container_ip $APP_SERVER)

    for i in {1..10}
    do
		sleep 1
        curl -s http://$APP_SERVER_IP:$PORT/dave.html >& /dev/null
	    if [ $? == 0 ]; then
		    break
	    fi
    done

    echo $APP_SERVER_IP
}

echo "Starting Nonce Store"
NONCE_STORE=$(create_nonce_store) 
echo $NONCE_STORE

echo "Starting App Server"
APP_SERVER=$(create_app_server)
echo $APP_SERVER

echo "Starting Key Store"
KEY_STORE=$(create_key_store) 
echo $KEY_STORE

echo "Starting Key Server"
KEY_SERVER=$(create_key_server $KEY_STORE)
echo $KEY_SERVER

exit 0
