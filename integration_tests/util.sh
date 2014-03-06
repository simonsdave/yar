# this file includes a collection of bash shell functions that
# felt generally reusable across a variety of bash shell scripts.
# the functions are introduced to the shell scripts with the
# following lines @ the top of the script
#
#	SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#	source $SCRIPT_DIR_NAME/util.sh

# generate an api key for use with basic authentication
# and then save the api key to a key store
create_basic_api_key() {
	local KEY_STORE=${1:-}
	
	local API_KEY=$(python -c "from yar.util.basic import APIKey; print APIKey.generate()")
	local CREDS="{\"principal\": \"dave@example.com\", \"type\": \"creds_v1.0\", \"is_deleted\": false, \"basic\": {\"api_key\": \"$API_KEY\"}}"
	local CONTENT_TYPE="Content-Type: application/json; charset=utf8"
	curl \
		-s \
		-X PUT \
		-H "$CONTENT_TYPE" \
		-d "$CREDS" \
		http://$KEY_STORE/$API_KEY \
		>& /dev/null
	if [ "$?" == "0" ]; then
		echo "$API_KEY"
	else
		echo ""
	fi
}

get_container_ip() {
    sudo docker inspect -format '{{ .NetworkSettings.IPAddress }}' ${1:-}
}

get_from_json() {
    PATTERN=${1:-}
    JSON.sh | \
        grep $PATTERN |
        sed -e "s/$PATTERN//" |
        sed -e "s/[[:space:]]//g" |
        sed -e "s/\"//g"
}

# create a docker container to run the app server
create_app_server() {

    DATA_DIRECTORY=$SCRIPT_DIR_NAME/App-Server/artifacts
    rm -rf $DATA_DIRECTORY >& /dev/null
    mkdir -p $DATA_DIRECTORY

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

# create a docker container to run the app server load balancer
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

# create a docker container to run the key store
create_key_store() {
    PORT=5984
    DATABASE=creds

    DATA_DIRECTORY=$SCRIPT_DIR_NAME/Key-Store/artifacts
    rm -rf $DATA_DIRECTORY >& /dev/null
    mkdir -p $DATA_DIRECTORY
	# :TODO: add check that docker images have been built
    KEY_STORE=$(sudo docker run -d -v $DATA_DIRECTORY:/usr/local/var/lib/couchdb:rw -t key_store_img)
    KEY_STORE_IP=$(sudo docker inspect -format '{{ .NetworkSettings.IPAddress }}' $KEY_STORE)

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

# create a docker container to run the key server
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

# create a docker container to run the nonce store
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

# create a docker container to run the auth_server
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

# create a docker container to run the auth server load balancer
create_auth_server_lb() {

    AUTH_SERVER=${1:-}

    PORT=8000

    CFG_TEMPLATE_DIRECTORY=$SCRIPT_DIR_NAME/Auth-Server-LB
    CFG_DIRECTORY=$CFG_TEMPLATE_DIRECTORY/artifacts
    rm -rf $CFG_DIRECTORY >& /dev/null
    mkdir $CFG_DIRECTORY
    cp $CFG_TEMPLATE_DIRECTORY/haproxy.cfg.template $CFG_DIRECTORY/haproxy.cfg
    echo "    server authserver1 $AUTH_SERVER check" >> $CFG_DIRECTORY/haproxy.cfg

    AUTH_SERVER_LB_CMD="haproxy -f /haproxycfg/haproxy.cfg"
    AUTH_SERVER_LB=$(sudo docker run -d -v /dev/log:/haproxy/log -v $CFG_DIRECTORY:/haproxycfg auth_server_lb_img $AUTH_SERVER_LB_CMD)
    AUTH_SERVER_LB_IP=$(get_container_ip $AUTH_SERVER_LB)

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
