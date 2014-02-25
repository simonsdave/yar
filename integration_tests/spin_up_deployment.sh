#!/usr/bin/env bash

# very useful for debugging ...
#
#   sudo docker run -i -t yar_img /bin/bash

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

get_container_ip() {
    sudo docker inspect -format '{{ .NetworkSettings.IPAddress }}' ${1:-}
}

get_from_json() {
    PATTERN=${1:-}
    CREATE_ACCOUNT_OUTPUT_FILE_NAME=${2:-}
    JSON.sh | \
        grep $PATTERN |
        sed -e "s/$PATTERN//" |
        sed -e "s/[[:space:]]//g" |
        sed -e "s/\"//g"
}

create_auth_server() {
    KEY_SERVER=${1:-}
    APP_SERVER=${2:-}
    NONCE_STORE=${3:-}
    PORT=8000
    AUTH_SERVER_CMD="auth_server --log=info --lon=$PORT --keyserver=$KEY_SERVER --appserver=$APP_SERVER --noncestore=$NONCE_STORE --syslog=/dev/log"
    AUTH_SERVER=$(sudo docker run -d -v /dev/log:/dev/log yar_img $AUTH_SERVER_CMD)
    AUTH_SERVER_IP=$(get_container_ip $AUTH_SERVER)

    for i in {1..10}
    do
        sleep 1
        curl -s http://$AUTH_SERVER_IP:$PORT >& /dev/null
        if [ $? == 0 ]; then
            break
        fi
    done

    echo $AUTH_SERVER_IP:$PORT
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
    KEY_SERVER_CMD="key_server --log=info --lon=$PORT --key_store=${1:-} --syslog=/dev/log"
    KEY_SERVER=$(sudo docker run -d -v /dev/log:/dev/log yar_img $KEY_SERVER_CMD)
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

    DATA_DIRECTORY=$SCRIPT_DIR_NAME/Key-Store-Data
    rm -rf $DATA_DIRECTORY >& /dev/null
    mkdir -p $DATA_DIRECTORY
    KEY_STORE=$(sudo docker run -d -v $DATA_DIRECTORY:/usr/local/var/lib/couchdb:rw -t key_store_img)
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
    APP_SERVER_CMD="app_server --log=info --lon=$PORT --syslog=/dev/log"
    APP_SERVER=$(sudo docker run -d -v /dev/log:/dev/log yar_img $APP_SERVER_CMD)
    APP_SERVER_IP=$(get_container_ip $APP_SERVER)

    for i in {1..10}
    do
        sleep 1
        curl -s http://$APP_SERVER_IP:$PORT/dave.html >& /dev/null
        if [ $? == 0 ]; then
            break
        fi
    done

    echo $APP_SERVER_IP:$PORT
}

create_app_server_lb() {

    APP_SERVER=${1:-}

    PORT=8080

    CFG_TEMPLATE_DIRECTORY=$SCRIPT_DIR_NAME/App-Server-LB
    CFG_DIRECTORY=$SCRIPT_DIR_NAME/App-Server-LB/artifacts
    rm -rf $CFG_DIRECTORY >& /dev/null
    mkdir $CFG_DIRECTORY
    cp $CFG_TEMPLATE_DIRECTORY/haproxy.cfg.template $CFG_DIRECTORY/haproxy.cfg
    echo "    server appserver1 $APP_SERVER check" >> $CFG_DIRECTORY/haproxy.cfg

    APP_SERVER_LB_CMD="haproxy -f /haproxycfg/haproxy.cfg"
    APP_SERVER_LB=$(sudo docker run -d -v /dev/log:/haproxy/log -v $CFG_DIRECTORY:/haproxycfg app_server_lb_img $APP_SERVER_LB_CMD)
    APP_SERVER_LB_IP=$(get_container_ip $APP_SERVER_LB)

    for i in {1..10}
    do
        sleep 1
        curl -s http://$APP_SERVER_LB_IP:$PORT/dave.html >& /dev/null
        if [ $? == 0 ]; then
            break
        fi
    done

    echo $APP_SERVER_LB_IP:$PORT
}

create_basic_creds() {

    KEY_SERVER=${1:-}
    PRINCIPAL=${2:-}

    CREDS_FILE_NAME=$(mktemp)

    curl \
        -s \
        -X POST \
        -H "Content-Type: application/json; charset=utf8" \
        -d "{\"principal\":\"$PRINCIPAL\", \"auth_scheme\":\"basic\"}" \
        http://$KEY_SERVER/v1.0/creds > $CREDS_FILE_NAME

    API_KEY=`cat $CREDS_FILE_NAME | get_from_json '\["basic"\,"api_key"\]'`

    rm -rf $CREDS_FILE_NAME >& /dev/null

    echo $API_KEY
}

create_mac_creds() {

    KEY_SERVER=${1:-}
    PRINCIPAL=${2:-}

    CREDS_FILE_NAME=$(mktemp)

    curl \
        -s \
        -X POST \
        -H "Content-Type: application/json; charset=utf8" \
        -d "{\"principal\":\"$PRINCIPAL\", \"auth_scheme\":\"hmac\"}" \
        http://$KEY_SERVER/v1.0/creds > $CREDS_FILE_NAME

    local MAC_ALGORITHM=`cat $CREDS_FILE_NAME | get_from_json \
        '\["hmac"\,"mac_algorithm"\]'`

    local MAC_KEY_IDENTIFIER=`cat $CREDS_FILE_NAME | get_from_json \
        '\["hmac"\,"mac_key_identifier"\]'`

    local MAC_KEY=`cat $CREDS_FILE_NAME | get_from_json \
        '\["hmac"\,"mac_key"\]'`

    rm -rf ~/.yar.creds >& /dev/null
    echo "MAC_KEY_IDENTIFIER=$MAC_KEY_IDENTIFIER" > ~/.yar.creds
    echo "MAC_KEY=$MAC_KEY" >> ~/.yar.creds
    echo "MAC_ALGORITHM=$MAC_ALGORITHM" >> ~/.yar.creds

    rm -rf $CREDS_FILE_NAME >& /dev/null
}

PRINCIPAL="dave@example.com"

# spin up services

echo "Starting App Server(s)"
APP_SERVER=$(create_app_server)
echo $APP_SERVER

echo "Starting App Server LB"
APP_SERVER_LB=$(create_app_server_lb $APP_SERVER)
echo $APP_SERVER_LB

echo "Starting Nonce Store"
NONCE_STORE=$(create_nonce_store) 
echo $NONCE_STORE

echo "Starting Key Store"
KEY_STORE=$(create_key_store) 
echo $KEY_STORE

echo "Starting Key Server"
KEY_SERVER=$(create_key_server $KEY_STORE)
echo $KEY_SERVER

echo "Starting Auth Server"
AUTH_SERVER=$(create_auth_server $KEY_SERVER $APP_SERVER_LB $NONCE_STORE)
echo $AUTH_SERVER

# services now running, time to provision some keys

echo ""
API_KEY=$(create_basic_creds $KEY_SERVER $PRINCIPAL)
echo "API key for basic auth = $API_KEY"

echo ""
create_mac_creds $KEY_SERVER $PRINCIPAL
echo "MAC creds in auth = ~/.yar.creds"
cat ~/.yar.creds

exit 0
