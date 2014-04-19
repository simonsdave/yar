# this file includes a collection of bash shell functions that
# felt generally reusable across a variety of bash shell scripts.
# the functions are introduced to the shell scripts with the
# following lines @ the top of the script
#
#	SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#	source $SCRIPT_DIR_NAME/util.sh

get_container_ip() {
    CONTAINER_ID=${1:-}
    sudo docker inspect --format '{{ .NetworkSettings.IPAddress }}' $CONTAINER_ID
}

get_from_json() {
    PATTERN=${1:-}
    VALUE_IF_NOT_FOUND=${2:-}

    VALUE=$(grep -v "^\\s*#" | JSON.sh | grep $PATTERN)

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
		echo_to_stderr "${1:-}"
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
# seems like a common'ish yar practice is to use JSON as a format
# for configuration files. this work just fine except that there's
# no good way to comment these files and comments are critical
# in all but the most trivial configuration file. the yar practice
# that has emerged is to use the JSON format but treat any lines
# that begin with a # as the first non-whitespace character as
# a comment.
#
# this function reads stdin, removes all lines that have a # character
# as the first non-whitespace character and apply "nice" formatting
# to the remaining lines assuming those lines represent a JSON file
#
# arguments
#   none
#
# exit codes
#   0   always
#
remove_comments_and_format_json() {
    # :TODO: what if stdin isn't a valid JSON file?
    grep -v '^\s*#' | python -mjson.tool
    return 0
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
# get the number of keys in ~/.yar.deployment matching a
# specified pattern
#
# for example, the following script gets the number of auth
# servers described in ~/.yar.deployment
#
#   #!/usr/bin/env bash
#   SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#   source $SCRIPT_DIR_NAME/util.sh
#   NUMBER_AUTH_SERVERS=$(get_number_deployment_config_keys "AUTH_SERVER_CONTAINER_ID_[[:digit:]]\+")
#   echo $NUMBER_AUTH_SERVERS
#
# arguments
#   1   pattern to search for
#
# exit codes
#   0   always
#
get_number_deployment_config_keys() {
    local PATTERN=${1:-}
    # :TODO: deal with spaces before and after key?
    local PATTERN="^$PATTERN\="
    if [ -r ~/.yar.deployment ]; then
        grep "$PATTERN" ~/.yar.deployment | wc -l
    else
        echo 0
    fi
    return 0
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

    local APP_SERVER_NUMBER=$(get_number_deployment_config_keys \
        "APP_SERVER_CONTAINER_ID_[[:digit:]]\+")
    let "APP_SERVER_NUMBER += 1"

    echo "APP_SERVER_CONTAINER_ID_$APP_SERVER_NUMBER=$APP_SERVER" >> ~/.yar.deployment
    echo "APP_SERVER_IP_$APP_SERVER_NUMBER=$APP_SERVER_IP" >> ~/.yar.deployment
    echo "APP_SERVER_END_POINT_$APP_SERVER_NUMBER=$APP_SERVER_IP:$PORT" >> ~/.yar.deployment

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
# echo to stdout each of the app server container ids
# list in ~/.yar.deployment
#
# example expected usage
#
#   #!/usr/bin/env bash
#   SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#   source $SCRIPT_DIR_NAME/util.sh
#   for ASID in $(get_all_app_server_container_ids); do
#       echo ">>>$ASID<<<"
#   done
#
# arguments
#   none
#
# exit codes
#   0   ok
#   1   too many app servers in ~/.yar.deployment
#
get_all_app_server_container_ids() {
    for APP_SERVER_NUMBER in {1..100}
    do
        local KEY="APP_SERVER_CONTAINER_ID_$APP_SERVER_NUMBER"
        local APP_SERVER_CONTAINER_ID=$(get_deployment_config "$KEY" "")
        if [ "$APP_SERVER_CONTAINER_ID" == "" ]; then
            return 0
        fi
        echo $KEY
    done
    return 1
}

#
# create a docker container to run an app server load balancer
#
# arguments
#   1   name of data directory - mkdir -p called on this name
#
# exit codes
#   0   ok
#   1   general/non-specific failure - app server container not started
#   2   can't find yar_img
#
create_app_server_lb() {

    local DATA_DIRECTORY=${1:-}
    mkdir -p $DATA_DIRECTORY

    local PORT=8080

    local IMAGE_NAME=haproxy_img
    if ! does_image_exist $IMAGE_NAME; then
        echo_to_stderr_if_not_silent "docker image '$IMAGE_NAME' does not exist"
        return 2
    fi

	cp "$SCRIPT_DIR_NAME/haproxy.cfg/app_server" "$DATA_DIRECTORY/haproxy.cfg"

	local APP_SERVER_NUMBER=1
	for APP_SERVER_CONTAINER_ID_KEY in $(get_all_app_server_container_ids)
	do
		APP_SERVER_CONTAINER_ID=$(get_deployment_config "$APP_SERVER_CONTAINER_ID_KEY")
		APP_SERVER_IP=$(get_container_ip "$APP_SERVER_CONTAINER_ID")
		echo "    server appserver$APP_SERVER_NUMBER $APP_SERVER_IP check" >> $DATA_DIRECTORY/haproxy.cfg
		let "APP_SERVER_NUMBER += 1"
	done

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

    local NONCE_STORE_NUMBER=$(get_number_deployment_config_keys \
        "NONCE_STORE_CONTAINER_ID_[[:digit:]]\+")
    let "NONCE_STORE_NUMBER += 1"

    echo "NONCE_STORE_CONTAINER_ID_$NONCE_STORE_NUMBER=$NONCE_STORE" >> ~/.yar.deployment
    echo "NONCE_STORE_IP_$NONCE_STORE_NUMBER=$NONCE_STORE_IP" >> ~/.yar.deployment
    echo "NONCE_STORE_END_POINT_$NONCE_STORE_NUMBER=$NONCE_STORE_IP:$PORT" >> ~/.yar.deployment

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
# echo to stdout each of the nonce store container ids
# list in ~/.yar.deployment
#
# example expected usage
#
#   #!/usr/bin/env bash
#   SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#   source $SCRIPT_DIR_NAME/util.sh
#   for NSCID in $(get_all_nonce_store_container_ids); do
#       echo ">>>$NSCID<<<"
#   done
#
# arguments
#   none
#
# exit codes
#   0   ok
#   1   too many nonce stores in ~/.yar.deployment
#
get_all_nonce_store_container_ids() {
    for NONCE_STORE_NUMBER in {1..100}
    do
        local KEY="NONCE_STORE_CONTAINER_ID_$NONCE_STORE_NUMBER"
        local NONCE_STORE_CONTAINER_ID=$(get_deployment_config "$KEY" "")
        if [ "$NONCE_STORE_CONTAINER_ID" == "" ]; then
            return 0
        fi
        echo $KEY
    done
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

    cp $SCRIPT_DIR_NAME/haproxy.cfg/auth_server $DATA_DIRECTORY/haproxy.cfg
    echo "    server authserver1 $AUTH_SERVER check" >> $DATA_DIRECTORY/haproxy.cfg

    local AUTH_SERVER_LB_CMD="haproxy -f /haproxycfg/haproxy.cfg"
    local AUTH_SERVER_LB=$(sudo docker run \
        -d \
		-p $PORT:$PORT \
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

#
# as the function's name says ... stop the mechanism used
# to collect container specific metrics
#
# exit status
#   0   ok
#   n   where n is non-zero indicates failure; n will be
#       the status code of "service collectd stop"
#
stop_collecting_metrics() {
    sudo service collectd stop >& /dev/null
}

#
# as the function's name says ... start the mechanism used
# to collect container specific metrics
#
# exit status
#   0   ok
#   n   where n is non-zero indicates failure; n will be
#       the status code of "service collectd restart"
#
start_collecting_metrics() {

    # this should be overkill as collectd should
    # already have been stopped
    sudo service collectd stop >& /dev/null

    # :TODO: /var/lib/collectd is embedded in 
    # /vagrant/collectd.cfg/collectd.conf.postfix
    # so a change in /vagrant/collectd.cfg/collectd.conf.postfix
    # won't be reflected in this code - should
    # only be defining this directory in one location
    sudo rm -rf /var/lib/collectd >& /dev/null

    TEMP_COLLECTD_CONF=$(platform_safe_mktemp)

    cat /vagrant/collectd.cfg/collectd.conf.prefix >> $TEMP_COLLECTD_CONF

	# NOTE - the if below will typically only fail if Docker's not been
	# instructed to use lxc
	if [ -d /sys/fs/cgroup/memory/lxc ]; then
		for PUSEDO_FILE in /sys/fs/cgroup/memory/lxc/*/memory.usage_in_bytes
		do
			CONTAINER_ID=$(echo $PUSEDO_FILE | \
				sed -e "s/^\/sys\/fs\/cgroup\/memory\/lxc\///" | \
				sed -e "s/\/memory.usage_in_bytes$//")

			cat /vagrant/collectd.cfg/collectd.conf.memory_usage | \
				sed -e "s/%CONTAINER_ID%/$CONTAINER_ID/g" \
				>> $TEMP_COLLECTD_CONF
		done
	fi

	# NOTE - the if below will typically only fail if Docker's not been
	# instructed to use lxc
	if [ -d /sys/fs/cgroup/cpuacct/lxc ]; then
		for PUSEDO_FILE in /sys/fs/cgroup/cpuacct/lxc/*/cpuacct.usage
		do
			CONTAINER_ID=$(echo $PUSEDO_FILE | \
				sed -e "s/^\/sys\/fs\/cgroup\/cpuacct\/lxc\///" | \
				sed -e "s/\/cpuacct.usage$//")

			cat /vagrant/collectd.cfg/collectd.conf.cpu_usage | \
				sed -e "s/%CONTAINER_ID%/$CONTAINER_ID/g" \
				>> $TEMP_COLLECTD_CONF
		done
	fi

    cat /vagrant/collectd.cfg/collectd.conf.postfix >> $TEMP_COLLECTD_CONF

    sudo mv $TEMP_COLLECTD_CONF /etc/collectd/collectd.conf

    sudo service collectd restart >& /dev/null
}

#
# assuming start_collecting_metrics() and stop_collecting_metrics()
# have been used to collect metrics, calling this function is used
# to generate a graph for the memory used by a particular container.
#
# arguments
#   1   graph's title
#   2   key @ which the container's id can be found
#   3   filename into which the graph should be generated
#
# exit codes
#   0   ok
#
gen_mem_usage_graph() {

    local GRAPH_TITLE=${1:-}
    local CONTAINER_ID_KEY=${2:-}
    local GRAPH_FILENAME=${3:-}

    CONTAINER_ID=$(get_deployment_config "$CONTAINER_ID_KEY")
    if [ "$CONTAINER_ID" == "" ]; then
        echo_to_stderr_if_not_silent "No container ID found for '$CONTAINER_ID_KEY'"
        return 1
    fi

    #
    # :TRICKY: there's a tricky bit of code in the line below related to
    # the way we take the first 16 characters of CONTAINER_ID. collectd
    # only seems to use the first 60'ish characters from the container ID
    # to create the output file directory. The first 16 characters are more
    # than enough to uniquely identify the directory. The reason for the
    # * on the end of the directory name is acknowledgement of the 60'ish
    # statement & the fact that 16 characters is more than enough to identity
    # the directory.
    #
    METRICS_DIR=/var/lib/collectd/csv/precise64/table-memory-${CONTAINER_ID:0:16}*
    if [ ! -d $METRICS_DIR ]; then
        echo_to_stderr_if_not_silent "Could not find memory metrics directory for '$CONTAINER_ID'"
        return 1
    fi

    #
    # take all collectd output files (which are all files in $METRICS_DIR
    # starting with gauge-), cat them into a single file and strip out the
    # "epoch,value" headers
    #
    OBSERVATIONS_1=$(platform_safe_mktemp)

    cat $METRICS_DIR/gauge-* | \
        grep "^[0-9]" | \
        sort --field-separator=$',' --key=1 -n \
        > $OBSERVATIONS_1

    #
    # so we've now got all the metrics in a single file order by time.
    # next step is to massage the metrics in preperation for graphing.
    #
    FIRST_TIME=$(head -1 $OBSERVATIONS_1 | sed -e "s/\,.\+$//g")

    AWK_PROG=$(platform_safe_mktemp)
    echo 'BEGIN       {FS = ","; OFS = ","}'                                >> $AWK_PROG
    echo '/^[0-9]+/   {print $1 - first_time, int(1 + $2/(1024.0*1024.0))}' >> $AWK_PROG

    OBSERVATIONS_2=$(platform_safe_mktemp)

    cat $OBSERVATIONS_1 | awk -v first_time=$FIRST_TIME -f $AWK_PROG > $OBSERVATIONS_2

    rm $AWK_PROG

    #
    # finally! let's generate a graph:-)
    #
    gnuplot \
        -e "input_filename='$OBSERVATIONS_2'" \
        -e "output_filename='$GRAPH_FILENAME'" \
        -e "title='$GRAPH_TITLE'" \
        $SCRIPT_DIR_NAME/gp.cfg/memory_usage \
        >& /dev/null
    if [ $? -ne 0 ]; then
        echo_to_stderr_if_not_silent "Error generating graph '$GRAPH_TITLE'"
    fi

    rm $OBSERVATIONS_1
    rm $OBSERVATIONS_2

    return 0
}

#
# assuming start_collecting_metrics() and stop_collecting_metrics()
# have been used to collect metrics, calling this function is used
# to generate a graph of CPU utilization a particular container.
#
# arguments
#   1   graph's title
#   2   key @ which the container's id can be found
#   3   filename into which the graph should be generated
#
# exit codes
#   0   ok
#   1   couldn't find container ID for supplied key (arg #2)
#
gen_cpu_usage_graph() {

    local GRAPH_TITLE=${1:-}
    local CONTAINER_ID_KEY=${2:-}
    local GRAPH_FILENAME=${3:-}

    CONTAINER_ID=$(get_deployment_config "$CONTAINER_ID_KEY")
    if [ "$CONTAINER_ID" == "" ]; then
        echo_to_stderr_if_not_silent "No container ID found for '$CONTAINER_ID_KEY'"
        return 1
    fi

    #
    # :TRICKY: there's a tricky bit of code in the line below related to
    # the way we take the first 16 characters of CONTAINER_ID. collectd
    # only seems to use the first 60'ish characters from the container ID
    # to create the output file directory. The first 16 characters are more
    # than enough to uniquely identify the directory. The reason for the
    # * on the end of the directory name is acknowledgement of the 60'ish
    # statement & the fact that 16 characters is more than enough to identity
    # the directory.
    #
    METRICS_DIR=/var/lib/collectd/csv/precise64/table-cpu-${CONTAINER_ID:0:16}*
    if [ ! -d $METRICS_DIR ]; then
        echo_to_stderr_if_not_silent "Could not find cpu metrics directory for '$CONTAINER_ID'"
        return 1
    fi

    #
    # take all collectd output files (which are all files in $METRICS_DIR
    # starting with gauge-), cat them into a single file and strip out the
    # "epoch,value" headers
    #
    OBSERVATIONS_1=$(platform_safe_mktemp)

    cat $METRICS_DIR/gauge-* | \
        grep "^[0-9]" | \
        sort --field-separator=$',' --key=1 -n \
        > $OBSERVATIONS_1

    #
    # so we've now got all the metrics in a single file order by time.
    # next step is to massage the metrics in preperation for graphing.
    #
    FIRST_TIME=$(head -1 $OBSERVATIONS_1 | sed -e "s/\,.\+$//g")

    OBSERVATIONS_2=$(platform_safe_mktemp)

    #
    # to understand the awk script below you need to have a firm grasp
    # of what /sys/fs/cgroup/cpuacct/lxc/*/cpuacct.usage is recording.
    # here's what the manual says:
    #
    #   total CPU time (in nanoseconds) consumed by all tasks in this cgroup
    #
    # as a reminder - nanosecond = 1 / 1,000,000,000 second
    #
    AWK_PROG=$(platform_safe_mktemp)
    echo 'BEGIN     {FS = ","; OFS = ","; prev_epoch = -1;}'   >> $AWK_PROG
    echo '/^[0-9]+/ {
                        if (prev_epoch < 0)
                        {
                            prev_epoch = $1
                            prev_usage = $2
                        }
                        else
                        {
                            cpu_time_used = $2 - prev_usage
                            cpu_time_available = number_cpus * ($1 - prev_epoch) * 1000000000.0
                            cpu_percentage = 100.0 * (cpu_time_used / cpu_time_available)

                            print prev_epoch - first_time, cpu_percentage

                            prev_epoch = $1
                            prev_usage = $2
                        }
                    }' >> $AWK_PROG

    OBSERVATIONS_2=$(platform_safe_mktemp)

    local NUMBER_CPUS=$(cat /sys/fs/cgroup/cpuacct/cpuacct.usage_percpu | wc -w)

    cat $OBSERVATIONS_1 | \
        awk -v first_time=$FIRST_TIME -v number_cpus=$NUMBER_CPUS -f $AWK_PROG \
        > $OBSERVATIONS_2

    rm $AWK_PROG

    #
    # finally! let's generate a graph:-)
    #
    gnuplot \
        -e "input_filename='$OBSERVATIONS_2'" \
        -e "output_filename='$GRAPH_FILENAME'" \
        -e "title='$GRAPH_TITLE'" \
        $SCRIPT_DIR_NAME/gp.cfg/cpu_usage \
        >& /dev/null
    if [ $? -ne 0 ]; then
        echo_to_stderr_if_not_silent "Error generating graph '$GRAPH_TITLE'"
    fi

    rm $OBSERVATIONS_1
    rm $OBSERVATIONS_2

    return 0
}

#
# if locust is used as the load driver in a load tests it will output
# metrics to stdout every 2 seconds. these metrics can be parsed so we
# can graph the requests/second and # of errors. this function
# encapsulates the logic of parsing locust's output and generating
# a graph.
#
# arguments
#   1   graph's title
#   2   filename with locust's stdout
#   3   filename into which the graph should be generated
#
# exit codes
#   0   ok
#
gen_rps_and_errors_graph() {

    local GRAPH_TITLE=${1:-}
    local LOCUST_STDOUT=${2:-}
    local GRAPH_FILENAME=${3:-}

    local AWK_PROG=$(platform_safe_mktemp)

    echo 'BEGIN {
                    FS=" ";
                    OFS="\t";
                    epoch=0;
                    prev_failures=0;
                }' >> $AWK_PROG
    #
    # :TRICKY: the "+= 2" is the result of locust generating
    # metrics every 2 seconds
    #
    echo '/GET/ {
                    split($4, failures, "(");
                    print epoch, $3, failures[1] - prev_failures, $10;
                    epoch += 2;
                    prev_failures = failures[1];
                }' >> $AWK_PROG

    local RPS_AND_ERRORS_DATA=$(platform_safe_mktemp)
    awk \
        -f $AWK_PROG \
        < $LOCUST_STDOUT \
        > $RPS_AND_ERRORS_DATA

    local SCRIPT_DIR_NAME="$( cd "$( dirname "$BASH_SOURCE" )" && pwd )"
    gnuplot \
        -e "input_filename='$RPS_AND_ERRORS_DATA'" \
        -e "output_filename='$GRAPH_FILENAME'" \
        -e "title='$GRAPH_TITLE'" \
        $SCRIPT_DIR_NAME/gp.cfg/requests_per_second_and_errors \
        >& /dev/null

    rm $RPS_AND_ERRORS_DATA
    rm $AWK_PROG
}
