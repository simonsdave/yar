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
    VALUE_IF_NOT_FOUND=${2:-}

    VALUE=$(JSON.sh | grep $PATTERN)

    if [ "$VALUE" == "" ]; then
        echo $VALUE_IF_NOT_FOUND
    fi

    echo $VALUE |
        sed -e "s/$PATTERN//" |
        sed -e "s/[[:space:]]//g" |
        sed -e "s/\"//g"
}

#
# write the first argument to this function (which is assumed
# to be a string) to stderr
#
# exit codes
#   0   always
#
echo_to_stderr() {
	echo ${1:-} >&2
	return 0
}

#
# a few BASH script should be able to run on both Ubuntu
# and OS X - mktemp operates slightly differently on these
# two platforms - this function insulates scripts from
# the differences
#
# exit codes
#   0   always
#
platform_safe_mktemp() {
	mktemp 2> /dev/null || mktemp -t DAS
	return 0
}

#
# if the variable $VERBOSE is 1 then the first argument to this
# function is assumed to be a string and the function echo's
# the string to stdout
#
# exit codes
#   0   always
#
echo_if_verbose() {
    if [ 1 -eq ${VERBOSE:-0} ]; then
        echo $1
    fi
    return 0
}

#
# if the variable $VERBOSE is 1 then the first argument to this
# function is assumed to be a file name and the function cats the
# contents of the file to stdout
#
# exit codes
#   0   always
#
cat_if_verbose() {
    if [ 1 -eq ${VERBOSE:-0} ]; then
        cat $1
    fi
    return 0
}

#
# if the variable $SILENT is not 0 then the first argument to this
# function is assumed to be a string and the function echo's
# the string to stdout
#
# exit codes
#   0   always
#
echo_if_not_silent() {
    if [ 0 -eq ${SILENT:-0} ]; then
        echo $1
    fi
    return 0
}

#
# if the variable $SILENT is not 0 then the first argument to this
# function is assumed to be a string and the function echo's
# the string to stdout
#
# exit codes
#   0   always
#
echo_to_stderr_if_not_silent() {
    if [ 0 -eq ${SILENT:-0} ]; then
		echo_to_stderr ${1:-}
    fi

    return 0
}

#
# if the variable $SILENT is not 0 then the first argument to this
# function is assumed to be a file name and the function cats the
# contents of the file to stdout
#
# exit codes
#   0   always
#
cat_if_not_silent() {
    if [ 0 -eq ${SILENT:-0} ]; then
        cat $1
    fi

    return 0
}

#
# test if a docker image exists in the local repo
#
# arguments
#   1   docker image name
#
# exit codes
#   0   image exists
#   1   image does not exist
#
does_image_exist() {
    local IMAGE_NAME=${1:-IAMGE_NAME_THAT_SHOULD_NEVER_EXIST}
    local IMAGE_EXISTS=$(sudo docker images | grep ^$IMAGE_NAME | wc -l)
    if [ "$IMAGE_EXISTS" == "0" ]; then
        return 1
    else
        return 0
    fi
}

#
# get the value associated with a key in ~/.yar.creds
#
# for example, the following script gets the API key from ~/.yar.creds
#
#   #!/usr/bin/env bash
#   SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#   source $SCRIPT_DIR_NAME/util.sh
#   API_KEY=$(get_creds_config "API_KEY")
#   echo $API_KEY
#
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

#
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
#
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

#
# given a value of length V, add N - V zeros to left pad the
# value so the resulting value is N digits long
#
# for example, the following script writes 000023 to stdout
#
#   #!/usr/bin/env bash
#   SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#   source $SCRIPT_DIR_NAME/util.sh
#   left_zero_pad 23 6
#
left_zero_pad() {
    VALUE=${1:-}
    DESIRED_NUMBER_DIGITS=${2:-}
    python -c "print ('0'*10+'$VALUE')[-$DESIRED_NUMBER_DIGITS:]"
}

#
# create a docker container to run an app server
#
# arguments
#   1   name of data directory - mkdir -p called on this name
#   2   port on which to run the app server (optional, default = 8080)
#
# exit codes
#   0   ok
#   1   general/non-specific failure - app server container not started
#   2   can't find yar_img
#
create_app_server() {

    local DATA_DIRECTORY=${1:-}
    mkdir -p $DATA_DIRECTORY

    local PORT=${2:-8080}

    local IMAGE_NAME=yar_img
    if ! does_image_exist $IMAGE_NAME; then
        echo_to_stderr_if_not_silent "docker image '$IMAGE_NAME' does not exist"
        return 2
    fi

    local APP_SERVER_CMD="app_server \
        --log=info \
        --lon=$PORT \
        --logfile=/var/yar_app_server/app_server_log"
    local APP_SERVER=$(sudo docker run \
        -d \
        -v $DATA_DIRECTORY:/var/yar_app_server \
        $IMAGE_NAME \
        $APP_SERVER_CMD)
    local APP_SERVER_IP=$(get_container_ip $APP_SERVER)

    echo "APP_SERVER_CONTAINER_ID=$APP_SERVER" >> ~/.yar.deployment
    echo "APP_SERVER_IP=$APP_SERVER_IP" >> ~/.yar.deployment
    echo "APP_SERVER_END_POINT=$APP_SERVER_IP:$PORT" >> ~/.yar.deployment

    for i in {1..10}
    do
        sleep 1
        if curl http://$APP_SERVER_IP:$PORT/dave.html >& /dev/null; then
            echo $APP_SERVER_IP:$PORT
            return 0
        fi
    done

    echo_to_stderr_if_not_silent "Could not verify availability of App Server on $APP_SERVER_IP:$PORT"
    return 1
}

#
# create a docker container to run an app server load balancer
#
# arguments
#   1   name of data directory - mkdir -p called on this name
#   2   the app server
#
# exit codes
#   0   ok
#   1   general/non-specific failure - app server container not started
#   2   can't find yar_img
#
create_app_server_lb() {

    local DATA_DIRECTORY=${1:-}
    mkdir -p $DATA_DIRECTORY

    # :TODO: this whole thing with port numbers, app
    # server & template isn't right - review and fix
    local APP_SERVER=${2:-}

    local PORT=8080

    local IMAGE_NAME=haproxy_img
    if ! does_image_exist $IMAGE_NAME; then
        echo_to_stderr_if_not_silent "docker image '$IMAGE_NAME' does not exist"
        return 2
    fi

    cp $SCRIPT_DIR_NAME/app_server_haproxy.cfg.template $DATA_DIRECTORY/haproxy.cfg
    echo "    server appserver1 $APP_SERVER check" >> $DATA_DIRECTORY/haproxy.cfg

    local APP_SERVER_LB_CMD="haproxy -f /haproxycfg/haproxy.cfg"
    local APP_SERVER_LB=$(sudo docker run \
        -d \
        -v /dev/log:/haproxy/log \
        -v $DATA_DIRECTORY:/haproxycfg \
        $IMAGE_NAME \
        $APP_SERVER_LB_CMD)
    local APP_SERVER_LB_IP=$(get_container_ip $APP_SERVER_LB)

    echo "APP_SERVER_LB_CONTAINER_ID=$APP_SERVER_LB" >> ~/.yar.deployment
    echo "APP_SERVER_LB_IP=$APP_SERVER_LB_IP" >> ~/.yar.deployment
    echo "APP_SERVER_LB_END_POINT=$APP_SERVER_LB_IP:$PORT" >> ~/.yar.deployment

    for i in {1..10}
    do
        sleep 1
        if curl http://$APP_SERVER_LB_IP:$PORT/dave.html >& /dev/null; then
            echo $APP_SERVER_LB_IP:$PORT
            return 0
        fi
    done

    echo_to_stderr_if_not_silent "Could not verify availability of App Server LB on $APP_SERVER_LB_IP:$PORT"
    return 1
}

#
# create a docker container with a key store running on
# port 5984 with a database called creds
#
# arguments
#   1   name of data directory - mkdir -p called on this name
#   2   seed the key store with this number of credentials - optional
#   3   'true' or 'false' indicating if design docs should be created
#
# exit codes
#   0   ok
#   1   general/non-specific failure - app server container not started
#   2   can't find couchdb_img
#   3   can't find yar_img
#
create_key_store() {

    local DATA_DIRECTORY=${1:-}
    mkdir -p $DATA_DIRECTORY

    local KEY_STORE_SIZE=${2:-}

    local CREATE_DESIGN_DOCS=${3:-true}

    local PORT=5984
    local DATABASE=creds

    mkdir -p $DATA_DIRECTORY/data
    if [ "$KEY_STORE_SIZE" != "" ]; then
        local SCRIPT_DIR_NAME="$( cd "$( dirname "$BASH_SOURCE" )" && pwd )"
        local COUCH_FILE=$SCRIPT_DIR_NAME/lots-of-creds/$KEY_STORE_SIZE.creds.couch
        if ! cp $COUCH_FILE $DATA_DIRECTORY/data/$DATABASE.couch >& /dev/null; then
            echo_to_stderr_if_not_silent "Couldn't use existing couch file '$COUCH_FILE'"
            return 4
        fi
    fi
    mkdir -p $DATA_DIRECTORY/log
    mkdir -p $DATA_DIRECTORY/run

    local IMAGE_NAME=couchdb_img
    if ! does_image_exist $IMAGE_NAME; then
        echo_to_stderr_if_not_silent "docker image '$IMAGE_NAME' does not exist"
        return 2
    fi

    local KEY_STORE=$(sudo docker run \
        -d \
        -v $DATA_DIRECTORY/data:/usr/local/var/lib/couchdb \
        -v $DATA_DIRECTORY/log:/usr/local/var/log/couchdb \
        -v $DATA_DIRECTORY/run:/usr/local/var/run/couchdb \
        $IMAGE_NAME)

    local KEY_STORE_IP=$(get_container_ip $KEY_STORE)

    echo "KEY_STORE_CONTAINER_ID=$KEY_STORE" >> ~/.yar.deployment
    echo "KEY_STORE_IP=$KEY_STORE_IP" >> ~/.yar.deployment
    echo "KEY_STORE_END_POINT=$KEY_STORE_IP:$PORT" >> ~/.yar.deployment

    #
    # wait for couchdb to start
    #
    for i in {1..10}
    do
        sleep 1
        if curl -s http://$KEY_STORE_IP:$PORT >& /dev/null; then

            #
            # couchdb has successfully started ...
            #

            #
            # if we've preloaded credentials into the key store
            # then we don't need to create a credentials database
            # but we should install all design docs
            #
            if [ "$KEY_STORE_SIZE" == "" ]; then

                local INSTALLER_CMD="key_store_installer \
                    --log=info \
                    --delete=false \
                    --create=true \
                    --createdesign=$CREATE_DESIGN_DOCS \
                    --host=$KEY_STORE_IP:$PORT \
                    --database=$DATABASE"

            else

                local INSTALLER_CMD="key_store_installer \
                    --log=info \
                    --delete=false \
                    --create=false \
                    --createdesign=true \
                    --host=$KEY_STORE_IP:$PORT \
                    --database=$DATABASE"

            fi

            local IMAGE_NAME=yar_img
            if ! does_image_exist $IMAGE_NAME; then
                echo_to_stderr_if_not_silent "docker image '$IMAGE_NAME' does not exist"
                return 3
            fi
            sudo docker run \
                -i $IMAGE_NAME \
                $INSTALLER_CMD \
                >& /dev/null

            #
            # confirm the database has been created
            #
            for i in {1..10}
            do
                sleep 1
                if curl -s http://$KEY_STORE_IP:$PORT/$DATABASE >& /dev/null; then

                    echo "KEY_STORE_DB=$KEY_STORE_IP:$PORT/$DATABASE" >> ~/.yar.deployment

                    echo $KEY_STORE_IP:$PORT/$DATABASE

                    return 0
                fi
            done

            echo_to_stderr_if_not_silent "Could not verify availability of Key Store's CouchDB database on $KEY_STORE_IP:$PORT/$DATABASE"
            return 3

        fi
    done

    echo_to_stderr_if_not_silent "Could not verify availability of CouchDB on Key Store on $KEY_STORE_IP:$PORT"
    return 4
}

#
# Given a key store and an integer value P from 1 to 100, select at
# random P percent of the key store's creds save the creds to
# ~/.yar.creds.random.set
# 
# arguments
#   1   key store - required - <ip>:<port>/<database>
#   2   % of key store's credentials to extract
#
# implementation details
#
# install the view which takes a hash of each set of
# creds and, in a deterministic manner, maps
# the hash to a number between 1 and 100 effectively
# dividing the cred space into 100 1 percent
# sets. repeatedly call the view to grab sets of
# creds and write those creds to ~/.yar.creds.random.set
#
extract_random_set_of_creds_from_key_store() {

    local KEY_STORE=${1:-}
    local PERCENT_OF_CREDS=${2:-}

    local CREDS_OUTPUT_FILE=~/.yar.creds.random.set

    rm -f $CREDS_OUTPUT_FILE >& /dev/null

    local SCRIPT_DIR_NAME="$( cd "$( dirname "$BASH_SOURCE" )" && pwd )"

    curl \
        -X PUT \
        -H "Content-Type: application/json; charset=utf8" \
        -d @$SCRIPT_DIR_NAME/lots-of-creds/random_set_of_creds.js \
        http://$KEY_STORE/_design/random_set_of_creds \
        >& /dev/null
    # :TODO: what if curl fails?

    let "END = 100 - $PERCENT_OF_CREDS + 1"
    START=$(shuf -i 1-$END -n 1)
    let "END = $START + $PERCENT_OF_CREDS - 1"
    for i in $(seq $START $END)
    do
        CREDS=$(platform_safe_mktemp)
        curl -s http://$KEY_STORE/_design/random_set_of_creds/_view/all?key=$i >& $CREDS
        # :TODO: what if curl fails?
        cat $CREDS | \
            grep '^{"id"' | \
            sed -e 's/^{"id":"//' | \
            sed -e 's/".*$//' \
            >> $CREDS_OUTPUT_FILE
        rm -f $CREDS >& /dev/null
    done

    # 
    # :TODO: sort out DELETE which does no work right now
    # because no doc rev id is supplied.
    #
    # think actually we want purge rather than DELETE although even purge
    # won't reclaim disk space according to:
    #
    #   http://couchdb.readthedocs.org/en/latest/api/database/misc.html
    # 
    curl \
        -X DELETE \
        http://$KEY_STORE/_design/random_set_of_creds \
        >& /dev/null
    # :TODO: what if curl fails?

    return 1
}

#
# create a docker container to run a key server
#
# arguments
#   1   name of data directory - mkdir -p called on this name
#   2   key store
#
# exit codes
#   0   ok
#   1   general/non-specific failure - app server container not started
#   2   can't find yar_img
#
create_key_server() {

    local DATA_DIRECTORY=${1:-}
    mkdir -p $DATA_DIRECTORY

    local KEY_STORE=${2:-}

    local PORT=8070

    local IMAGE_NAME=yar_img
    if ! does_image_exist $IMAGE_NAME; then
        echo_to_stderr_if_not_silent "docker image '$IMAGE_NAME' does not exist"
        return 2
    fi

    local KEY_SERVER_CMD="key_server \
        --log=info \
        --lon=$PORT \
        --key_store=$KEY_STORE \
        --logfile=/var/yar_key_server/key_server_log"
    local KEY_SERVER=$(sudo docker run \
        -d \
        -v $DATA_DIRECTORY:/var/yar_key_server \
        $IMAGE_NAME \
        $KEY_SERVER_CMD)
    local KEY_SERVER_IP=$(get_container_ip $KEY_SERVER)

    echo "KEY_SERVER_CONTAINER_ID=$KEY_SERVER" >> ~/.yar.deployment
    echo "KEY_SERVER_IP=$KEY_SERVER_IP" >> ~/.yar.deployment
    echo "KEY_SERVER_END_POINT=$KEY_SERVER_IP:$PORT" >> ~/.yar.deployment

    for i in {1..10}
    do
        sleep 1
        if curl -s http://$KEY_SERVER_IP:$PORT/v1.0/creds >& /dev/null; then
            echo $KEY_SERVER_IP:$PORT
            return 0
        fi
    done

    echo_to_stderr_if_not_silent "Could not verify availability of Key Server on $KEY_SERVER_IP:$PORT"
    return 1
}

#
# create a docker container to run a nonce store
#
# arguments
#   1   name of data directory - mkdir -p called on this name
#   2   port on which to run the nonce store (optional, default = 11211)
#   3   MB of RAM for nonce store to use to store nonces (optional, default = 128)
#
# exit codes
#   0   ok
#   1   general/non-specific failure - nonce store container not started
#   2   can't find memcached_img
#
create_nonce_store() {

    local DATA_DIRECTORY=${1:-}
    mkdir -p $DATA_DIRECTORY

    local PORT=${2:-11211}

    local RAM=${3:-128}

    local IMAGE_NAME=memcached_img
    if ! does_image_exist $IMAGE_NAME; then
        echo_to_stderr_if_not_silent "docker image '$IMAGE_NAME' does not exist"
        return 2
    fi

    local NONCE_STORE_CMD="memcached.sh \
        $PORT \
        $RAM \
        /var/nonce_store/nonce_store_log"
    local NONCE_STORE=$(sudo docker run \
        -d \
        -v $DATA_DIRECTORY:/var/nonce_store \
        $IMAGE_NAME \
        $NONCE_STORE_CMD)
    local NONCE_STORE_IP=$(get_container_ip $NONCE_STORE)

    echo "NONCE_STORE_CONTAINER_ID=$NONCE_STORE" >> ~/.yar.deployment
    echo "NONCE_STORE_IP=$NONCE_STORE_IP" >> ~/.yar.deployment
    echo "NONCE_STORE_END_POINT=$NONCE_STORE_IP:$PORT" >> ~/.yar.deployment

    for i in {1..10}
    do
        sleep 1
        if echo stats | nc $NONCE_STORE_IP $PORT >& /dev/null; then
            echo $NONCE_STORE_IP:$PORT
            return 0
        fi
    done

    echo_to_stderr_if_not_silent "Could not verify availability of Nonce Store on $NONCE_STORE_IP:$PORT"
    return 1
}

#
# create a docker container to run an auth_server
#
# arguments
#   1   name of data directory - mkdir -p called on this name
#   2   key server
#   3   app server
#   4   nonce store
#
# exit codes
#   0   ok
#   1   general/non-specific failure - nonce store container not started
#   2   can't find yar_img
#
create_auth_server() {

    local DATA_DIRECTORY=${1:-}
    mkdir -p $DATA_DIRECTORY

    local KEY_SERVER=${2:-}
    local APP_SERVER=${3:-}
    local NONCE_STORE=${4:-}

    local PORT=8000

    local IMAGE_NAME=yar_img
    if ! does_image_exist $IMAGE_NAME; then
        echo_to_stderr_if_not_silent "docker image '$IMAGE_NAME' does not exist"
        return 2
    fi

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
        $IMAGE_NAME \
        $AUTH_SERVER_CMD)
    local AUTH_SERVER_IP=$(get_container_ip $AUTH_SERVER)

    echo "AUTH_SERVER_CONTAINER_ID=$AUTH_SERVER" >> ~/.yar.deployment
    echo "AUTH_SERVER_IP=$AUTH_SERVER_IP" >> ~/.yar.deployment
    echo "AUTH_SERVER_END_POINT=$AUTH_SERVER_IP:$PORT" >> ~/.yar.deployment

    for i in {1..10}
    do
        sleep 1
        if curl -s http://$AUTH_SERVER_IP:$PORT >& /dev/null; then
            echo $AUTH_SERVER_IP:$PORT
            return 0
        fi
    done

    echo_to_stderr_if_not_silent "Could not verify availability of Auth Server on $AUTH_SERVER_IP:$PORT"
    return 1
}

# create a docker container to run the auth server load balancer
create_auth_server_lb() {

    local DATA_DIRECTORY=${1:-}
    mkdir -p $DATA_DIRECTORY

    local AUTH_SERVER=${2:-}

    local PORT=8000

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
    echo "AUTH_SERVER_LB_END_POINT=$AUTH_SERVER_LB_IP:$PORT" >> ~/.yar.deployment

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
