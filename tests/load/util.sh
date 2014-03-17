# this file includes a collection of bash shell functions that
# felt generally reusable across a variety of bash shell scripts.
# the functions are introduced to the shell scripts with the
# following lines @ the top of the script
#
#	SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#	source $SCRIPT_DIR_NAME/util.sh

get_container_ip() {
    sudo docker inspect --format '{{ .NetworkSettings.IPAddress }}' ${1:-}
}

get_from_json() {
    PATTERN=${1:-}
    JSON.sh | \
        grep $PATTERN |
        sed -e "s/$PATTERN//" |
        sed -e "s/[[:space:]]//g" |
        sed -e "s/\"//g"
}

# get the value associated with a key in ~/.yar.creds
#
# for example, the following script gets the API key from ~/.yar.creds
#
#   #!/usr/bin/env bash
#   SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#   source $SCRIPT_DIR_NAME/util.sh
#   API_KEY=$(get_creds_config "API_KEY")
#   echo $API_KEY
get_creds_config() {
    local KEY=${1:-}
    local VALUE_IF_NOT_FOUND=${2:-}
    local VALUE=`grep "^\\s*$KEY\\s*=" ~/.yar.creds | \
        sed -e "s/^[[:space:]]*$KEY[[:space:]]*=[[:space:]]*//"`
    if [ "$VALUE" == "" ]; then
        echo $VALUE_IF_NOT_FOUND
    else
        echo $VALUE
    fi
}

# get the value associated with a key in ~/.yar.deployment
#
# for example, the following script gets the auth server
# container ID from ~/.yar.deployment
#
#   #!/usr/bin/env bash
#   SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#   source $SCRIPT_DIR_NAME/util.sh
#   AUTH_SERVER_CONTAINER_ID=$(get_deployment_config "AUTH_SERVER_CONTAINER_ID")
#   echo $AUTH_SERVER_CONTAINER_ID
get_deployment_config() {
    local KEY=${1:-}
    local VALUE_IF_NOT_FOUND=${2:-}
    local VALUE=`grep "^\\s*$KEY\\s*=" ~/.yar.deployment | \
        sed -e "s/^[[:space:]]*$KEY[[:space:]]*=[[:space:]]*//"`
    if [ "$VALUE" == "" ]; then
        echo $VALUE_IF_NOT_FOUND
    else
        echo $VALUE
    fi
}

# given a value of length V, add N - V zeros to left pad the
# value so the resulting value is N digits long
#
# for example, the following script writes 000023 to stdout
#
#   #!/usr/bin/env bash
#   SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#   source $SCRIPT_DIR_NAME/util.sh
#   left_zero_pad 23 6
left_zero_pad() {
    VALUE=${1:-}
    DESIRED_NUMBER_DIGITS=${2:-}
    python -c "print ('0'*10+'$VALUE')[-$DESIRED_NUMBER_DIGITS:]"
}

# create a docker container to run the app server
create_app_server() {

    local DATA_DIRECTORY=${1:-}
    mkdir -p $DATA_DIRECTORY

    local PORT=8080
    local APP_SERVER_CMD="app_server \
        --log=info \
        --lon=$PORT \
        --logfile=/var/yar_app_server/app_server_log"
    local APP_SERVER=$(sudo docker run \
        -d \
        -v $DATA_DIRECTORY:/var/yar_app_server \
        yar_img \
        $APP_SERVER_CMD)
    local APP_SERVER_IP=$(get_container_ip $APP_SERVER)

    echo "APP_SERVER_CONTAINER_ID=$APP_SERVER" >> ~/.yar.deployment
    echo "APP_SERVER_IP=$APP_SERVER_IP" >> ~/.yar.deployment

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

# create a docker container to run the app server load balancer
create_app_server_lb() {

    local DATA_DIRECTORY=${1:-}
    mkdir -p $DATA_DIRECTORY

    local APP_SERVER=${2:-}

    cp $SCRIPT_DIR_NAME/app_server_haproxy.cfg.template $DATA_DIRECTORY/haproxy.cfg
    echo "    server appserver1 $APP_SERVER check" >> $DATA_DIRECTORY/haproxy.cfg

    local APP_SERVER_LB_CMD="haproxy -f /haproxycfg/haproxy.cfg"
    local APP_SERVER_LB=$(sudo docker run \
        -d \
        -v /dev/log:/haproxy/log \
        -v $DATA_DIRECTORY:/haproxycfg \
        haproxy_img \
        $APP_SERVER_LB_CMD)
    local APP_SERVER_LB_IP=$(get_container_ip $APP_SERVER_LB)

    echo "APP_SERVER_LB_CONTAINER_ID=$APP_SERVER_LB" >> ~/.yar.deployment
    echo "APP_SERVER_LB_IP=$APP_SERVER_LB_IP" >> ~/.yar.deployment

    local PORT=8080

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

# create a docker container to run the key store
create_key_store() {

    local DATA_DIRECTORY=${1:-}
    mkdir -p $DATA_DIRECTORY

    local PORT=5984
    local DATABASE=creds

	# :TODO: add check that docker images have been built
    local KEY_STORE=$(sudo docker run \
        -d \
        -v $DATA_DIRECTORY:/usr/local/var/lib/couchdb:rw \
        -t \
        couchdb_img)
    local KEY_STORE_IP=$(get_container_ip $KEY_STORE)

    echo "KEY_STORE_CONTAINER_ID=$KEY_STORE" >> ~/.yar.deployment
    echo "KEY_STORE_IP=$KEY_STORE_IP" >> ~/.yar.deployment

    for i in {1..10}
    do
        sleep 1
        curl -s http://$KEY_SERVER_IP:$PORT >& /dev/null
        if [ $? == 0 ]; then
            break
        fi
    done

    local INSTALLER_CMD="key_store_installer \
        --log=info \
        --create=true \
        --host=$KEY_STORE_IP:$PORT \
        --database=$DATABASE"
    sudo docker run -i -t yar_img $INSTALLER_CMD >& /dev/null

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

# create a docker container to run the key server
create_key_server() {

    local DATA_DIRECTORY=${1:-}
    mkdir -p $DATA_DIRECTORY

    local KEY_STORE=${2:-}

    local PORT=8070
    local KEY_SERVER_CMD="key_server \
        --log=info \
        --lon=$PORT \
        --key_store=$KEY_STORE \
        --logfile=/var/yar_key_server/key_server_log"
    local KEY_SERVER=$(sudo docker run \
        -d \
        -v $DATA_DIRECTORY:/var/yar_key_server \
        yar_img \
        $KEY_SERVER_CMD)
    local KEY_SERVER_IP=$(get_container_ip $KEY_SERVER)

    echo "KEY_SERVER_CONTAINER_ID=$KEY_SERVER" >> ~/.yar.deployment
    echo "KEY_SERVER_IP=$KEY_SERVER_IP" >> ~/.yar.deployment

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

# create a docker container to run the nonce store
create_nonce_store() {

    local PORT=11211
    local NONCE_STORE_CMD=""
    local NONCE_STORE=$(sudo docker run \
        -d \
        memcached_img \
        $NONCE_STORE_CMD)
    local NONCE_STORE_IP=$(get_container_ip $NONCE_STORE)

    echo "NONCE_STORE_CONTAINER_ID=$NONCE_STORE" >> ~/.yar.deployment
    echo "NONCE_STORE_IP=$NONCE_STORE_IP" >> ~/.yar.deployment

    for i in {1..10}
    do
        sleep 1
        if [ "$(memcstat --servers=$NONCE_STORE_IP:$PORT | wc -l)" != "0" ]; then
            break
        fi
    done

    echo $NONCE_STORE_IP:$PORT
}

# create a docker container to run the auth_server
create_auth_server() {

    local DATA_DIRECTORY=${1:-}
    mkdir -p $DATA_DIRECTORY

    local KEY_SERVER=${2:-}
    local APP_SERVER=${3:-}
    local NONCE_STORE=${4:-}

    local PORT=8000
    local AUTH_SERVER_CMD="auth_server \
        --log=info \
        --lon=$PORT \
        --keyserver=$KEY_SERVER \
        --appserver=$APP_SERVER \
        --noncestore=$NONCE_STORE \
        --logfile=/var/auth_server/auth_server_log"
    local AUTH_SERVER=$(sudo docker run \
        -d \
        -v $DATA_DIRECTORY:/var/auth_server \
        yar_img \
        $AUTH_SERVER_CMD)
    local AUTH_SERVER_IP=$(get_container_ip $AUTH_SERVER)

    echo "AUTH_SERVER_CONTAINER_ID=$AUTH_SERVER" >> ~/.yar.deployment
    echo "AUTH_SERVER_IP=$AUTH_SERVER_IP" >> ~/.yar.deployment

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

# create a docker container to run the auth server load balancer
create_auth_server_lb() {

    local DATA_DIRECTORY=${1:-}
    mkdir -p $DATA_DIRECTORY

    local AUTH_SERVER=${2:-}

    cp $SCRIPT_DIR_NAME/auth_server_haproxy.cfg.template $DATA_DIRECTORY/haproxy.cfg
    echo "    server authserver1 $AUTH_SERVER check" >> $DATA_DIRECTORY/haproxy.cfg

    local AUTH_SERVER_LB_CMD="haproxy -f /haproxycfg/haproxy.cfg"
    local AUTH_SERVER_LB=$(sudo docker run \
        -d \
        -v /dev/log:/haproxy/log \
        -v $DATA_DIRECTORY:/haproxycfg \
        haproxy_img \
        $AUTH_SERVER_LB_CMD)
    local AUTH_SERVER_LB_IP=$(get_container_ip $AUTH_SERVER_LB)

    echo "AUTH_SERVER_LB_CONTAINER_ID=$AUTH_SERVER_LB" >> ~/.yar.deployment
    echo "AUTH_SERVER_LB_IP=$AUTH_SERVER_LB_IP" >> ~/.yar.deployment

    local PORT=8000

    for i in {1..10}
    do
        sleep 1
        curl -s http://$AUTH_SERVER_LB_IP:$PORT/dave.html >& /dev/null
        if [ $? == 0 ]; then
            break
        fi
    done

    echo $AUTH_SERVER_LB_IP:$PORT
}
