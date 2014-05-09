# this file includes a collection of bash shell functions that
# felt generally reusable across a variety of bash shell scripts.
# the functions are introduced to the shell scripts with the
# following lines @ the top of the script assuming this file
# is in the same directory as the script.
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
# to be a string) to stdout in yellow
#
# exit codes
#   0   always
#
echo_in_yellow() {
	echo "$(tput setaf 3)${1:-}$(tput sgr0)" 
	return 0
}

#
# write the first argument to this function (which is assumed
# to be a string) to stdout in red
#
# exit codes
#   0   always
#
echo_in_red() {
	echo "$(tput setaf 1)${1:-}$(tput sgr0)" 
	return 0
}

#
# write the first argument to this function (which is assumed
# to be a string) to stdout in blue
#
# exit codes
#   0   always
#
echo_in_blue() {
	echo "$(tput setaf 4)${1:-}$(tput sgr0)" 
	return 0
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

# # a few BASH script should be able to run on both Ubuntu
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
# a few BASH script should be able to run on both Ubuntu
# and OS X - mktemp operates slightly differently on these
# two platforms - this function insulates scripts from
# the differences
#
# exit codes
#   0   always
#
platform_safe_mktemp_directory() {
	mktemp -d 2> /dev/null || mktemp -d -t DAS
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
# just like the function name says, initialize things in preperation
# for spinning up a yar deployment
#
# arguments
#   1   directory in which deployment will be spun up
#
# exit codes
#   0   always
#
yar_init_deployment() {
    local DEPLOYMENT_LOCATION=${1:-}

    echo_if_not_silent "$(tput setaf 3)Initalizating Deployment$(tput sgr0)"

    echo_if_not_silent "-- Removing all existing containers"
    local SCRIPT_DIR_NAME="$( cd "$( dirname "$BASH_SOURCE" )" && pwd )"
    if ! $SCRIPT_DIR_NAME/rm_all_containers.sh; then
        echo_to_stderr_if_not_silent "-- Error removing all existing containers"
        return 1
    fi

    echo_if_not_silent "-- Removing '~/.yar.deployment'"
    rm -f ~/.yar.deployment >& /dev/null

    echo_if_not_silent "-- Removing '~/.yar.creds'"
    rm -f ~/.yar.creds >& /dev/null

    echo_if_not_silent "-- Removing '~/.yar.creds.random.set'"
    rm -f ~/.yar.creds.random.set >& /dev/null

    echo_if_not_silent "-- Deployment Location '$DEPLOYMENT_LOCATION'"
    echo "DEPLOYMENT_LOCATION=$DEPLOYMENT_LOCATION"  >> ~/.yar.deployment

    return 0
}

#
# create a docker container to run an app server
#
# arguments
#   none
#
# exit codes
#   0   ok
#   1   general/non-specific failure - app server container not started
#   2   can't find yar_img
#
create_app_server() {

    #
    # extract function arguments and setup function specific config
    #
    local DEPLOYMENT_LOCATION=$(get_deployment_config "DEPLOYMENT_LOCATION")

    local APP_SERVER_NUMBER=$(get_number_deployment_config_keys \
        "APP_SERVER_CONTAINER_ID_[[:digit:]]\+")
    let "APP_SERVER_NUMBER += 1"

    local DATA_DIRECTORY=$DEPLOYMENT_LOCATION/App-Server-$APP_SERVER_NUMBER
    mkdir -p $DATA_DIRECTORY

    local PORT=8080

    #
    # ...
    #
    local IMAGE_NAME=yar_img
    if ! does_image_exist $IMAGE_NAME; then
        echo_to_stderr_if_not_silent "docker image '$IMAGE_NAME' does not exist"
        return 2
    fi

    local APP_SERVER_CMD="app_server \
        --log=info \
        --lon=$PORT \
        --logfile=/var/yar_app_server/app_server_log"
    local DOCKER_RUN_STDERR=$DATA_DIRECTORY/docker_run_stderr
    local APP_SERVER=$(sudo docker run \
        -d \
        --name="App_Server_$APP_SERVER_NUMBER" \
        -v $DATA_DIRECTORY:/var/yar_app_server \
        $IMAGE_NAME \
        $APP_SERVER_CMD 2> "$DOCKER_RUN_STDERR")
    if [ "$APP_SERVER" == "" ]; then
        local MSG="Error starting App Server container"
        MSG="$MSG - error details in '$DOCKER_RUN_STDERR'"
        echo_to_stderr_if_not_silent "$MSG"
        return 2
    fi
    local APP_SERVER_IP=$(get_container_ip $APP_SERVER)

    echo "APP_SERVER_CONTAINER_ID_$APP_SERVER_NUMBER=$APP_SERVER" >> ~/.yar.deployment
    echo "APP_SERVER_IP_$APP_SERVER_NUMBER=$APP_SERVER_IP" >> ~/.yar.deployment
    echo "APP_SERVER_END_POINT_$APP_SERVER_NUMBER=$APP_SERVER_IP:$PORT" >> ~/.yar.deployment

    #
    # ...
    #
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
# echo to stdout each of the app server container id keys
# listed in ~/.yar.deployment
#
# example expected usage
#
#   #!/usr/bin/env bash
#   SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#   source $SCRIPT_DIR_NAME/util.sh
#   for ASIDK in $(get_all_app_server_container_id_keys); do
#       echo ">>>$ASIDK<<<"
#   done
#
# arguments
#   none
#
# exit codes
#   0   ok
#   1   too many app servers in ~/.yar.deployment
#
get_all_app_server_container_id_keys() {
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
# write stats about each app server to stdout. these stats are
# extracted from the app server load balancer
#
# arguments
#   none
#
# exit codes
#   0   ok
#   1   couldn't find app server LB container ID
#
get_app_server_stats() {

    APP_SERVER_LB_ADMIN_SOCKET=$(get_deployment_config "APP_SERVER_LB_ADMIN_SOCKET" "")
    if [ "$APP_SERVER_LB_ADMIN_SOCKET" == "" ]; then
        echo_to_stderr_if_not_silent "Could not find App Server LB admin socket"
        exit 1
    fi

    echo "show stat" | \
        sudo socat "$APP_SERVER_LB_ADMIN_SOCKET" stdio | \
        grep "^\(#\|app_server_lb,app_server_\)"
    exit 0
}

#
# create a docker container to run an app server load balancer
#
# arguments
#   none
#
# exit codes
#   0   ok
#   1   general/non-specific failure - app server container not started
#   2   can't find yar_img
#
create_app_server_lb() {

    #
    # extract function arguments and setup function specific config
    #
    local DEPLOYMENT_LOCATION=$(get_deployment_config "DEPLOYMENT_LOCATION")

    local DATA_DIRECTORY=$DEPLOYMENT_LOCATION/App-Server-LB
    mkdir -p $DATA_DIRECTORY

    local PORT=8080

    #
    # if we're spinning up a new haproxy or reconfiguring an existing
    # haproxy we're going to need to generate an haproxy configuration
    # file so let's get that over with
    #
    # http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#server
    # http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#5-weight
    # http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#5-check
    #
    local HAPROXY_CFG_FILENAME="$DATA_DIRECTORY/cfg-haproxy"

	cp "$SCRIPT_DIR_NAME/cfg-haproxy/app_server" "$HAPROXY_CFG_FILENAME"

	local APP_SERVER_NUMBER=1
	for APP_SERVER_CONTAINER_ID_KEY in $(get_all_app_server_container_id_keys)
	do
		APP_SERVER_CONTAINER_ID=$(get_deployment_config "$APP_SERVER_CONTAINER_ID_KEY")
		APP_SERVER_IP=$(get_container_ip "$APP_SERVER_CONTAINER_ID")
		echo "    server app_server_$APP_SERVER_NUMBER $APP_SERVER_IP check weight 100" >> "$HAPROXY_CFG_FILENAME"
		let "APP_SERVER_NUMBER += 1"
	done

    #
    # if no LB exists spin one up
    # if a LB does exist reload the new configuration
    #
    APP_SERVER_LB_CONTAINER_ID=$(get_deployment_config "APP_SERVER_LB_CONTAINER_ID" "")
    if [ "$APP_SERVER_LB_CONTAINER_ID" == "" ]; then

        local IMAGE_NAME=haproxy_img
        if ! does_image_exist $IMAGE_NAME; then
            echo_to_stderr_if_not_silent "docker image '$IMAGE_NAME' does not exist"
            return 2
        fi

        local APP_SERVER_LB_CMD="haproxy.sh /haproxy/cfg-haproxy /haproxy/haproxy.pid"
        local DOCKER_RUN_STDERR=$DATA_DIRECTORY/docker_run_stderr
        # haproxy's stats socket had to be created in a directory
        # that was guarenteed to be somewhere other than /vagrant
        local HAPROXY_ADMIN_DIR=$(mktemp -d)
        local APP_SERVER_LB_CONTAINER_ID=$(sudo docker run \
            -d \
            --name="App_Server_LB" \
            -p $PORT:$PORT \
            -v $DATA_DIRECTORY:/haproxy \
            -v $HAPROXY_ADMIN_DIR:/haproxy_admin \
            $IMAGE_NAME \
            $APP_SERVER_LB_CMD 2> "$DOCKER_RUN_STDERR")
        if [ "$APP_SERVER_LB_CONTAINER_ID" == "" ]; then
            local MSG="Error starting App Server LB container"
            MSG="$MSG - error details in '$DOCKER_RUN_STDERR'"
            echo_to_stderr_if_not_silent "$MSG"
            return 2
        fi
        local APP_SERVER_LB_IP=$(get_container_ip $APP_SERVER_LB_CONTAINER_ID)

        echo "APP_SERVER_LB_DEPLOYMENT_LOCATION=$DATA_DIRECTORY" >> ~/.yar.deployment
        # line below works because -v on /haproxy in above docker run
        # command and "stats socket /haproxy_admin/admin.sock level admin" in
        # the haproxy config file
        echo "APP_SERVER_LB_ADMIN_SOCKET=$HAPROXY_ADMIN_DIR/admin.sock" >> ~/.yar.deployment
        echo "APP_SERVER_LB_CONTAINER_ID=$APP_SERVER_LB_CONTAINER_ID" >> ~/.yar.deployment
        echo "APP_SERVER_LB_IP=$APP_SERVER_LB_IP" >> ~/.yar.deployment
        echo "APP_SERVER_LB_END_POINT=$APP_SERVER_LB_IP:$PORT" >> ~/.yar.deployment

    else

        local HAPROXY_RESTART_CMD='haproxy'
        HAPROXY_RESTART_CMD=$HAPROXY_RESTART_CMD' -f /haproxy/cfg-haproxy'
        HAPROXY_RESTART_CMD=$HAPROXY_RESTART_CMD' -p /haproxy/haproxy.pid'
        HAPROXY_RESTART_CMD=$HAPROXY_RESTART_CMD' -sf $(cat /haproxy/haproxy.pid)'

        echo $HAPROXY_RESTART_CMD | sudo lxc-attach --name=$APP_SERVER_LB_CONTAINER_ID

    fi

    #
    # the app server should now be able to respond to simple requests.
    # we'll use such a request to confirm the LB is up and running.
    #
    local APP_SERVER_LB_IP=$(get_container_ip $APP_SERVER_LB_CONTAINER_ID)

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
# arguments (all optional)
#   1   seed the key store with this number of credentials
#   2   percent of credentials for basic authentication
#   3   'true' or 'false' indicating if design docs should be created
#
# exit codes
#   0   ok
#   1   general/non-specific failure - app server container not started
#   2   can't find couchdb_img
#   3   can't find yar_img
#   4   DEPLOYMENT_LOCATION not found
#
create_key_store() {

    #
    # extract function arguments and setup function specific config
    #
    local DEPLOYMENT_LOCATION=$(get_deployment_config "DEPLOYMENT_LOCATION")
    if [ "$DEPLOYMENT_LOCATION" == "" ]; then
        echo_to_stderr_if_not_silent "Couldn not find DEPLOYMENT_LOCATION to start Key Store"
        return 4
    fi

    local DATA_DIRECTORY=$DEPLOYMENT_LOCATION/Key-Store
    mkdir -p $DATA_DIRECTORY

    local KEY_STORE_SIZE=${1:-}

    local PERCENT_BASIC_CREDS=${2:-}

    local CREATE_DESIGN_DOCS=${3:-true}

    local PORT=5984
    local DATABASE=creds

    #
    # if requested to do so, seed the key store with (a large
    # number of) credentials
    #
    mkdir -p $DATA_DIRECTORY/data
    if [ "$KEY_STORE_SIZE" != "" ]; then
        local SCRIPT_DIR_NAME="$( cd "$( dirname "$BASH_SOURCE" )" && pwd )"
        local COUCH_FILE=$SCRIPT_DIR_NAME/lots-of-creds/$KEY_STORE_SIZE.$PERCENT_BASIC_CREDS.creds.couch
        if ! cp $COUCH_FILE $DATA_DIRECTORY/data/$DATABASE.couch >& /dev/null; then
            echo_to_stderr_if_not_silent "Couldn't find couch file '$COUCH_FILE'"
            return 4
        fi
    fi
    mkdir -p $DATA_DIRECTORY/log
    mkdir -p $DATA_DIRECTORY/run

    #
    # spin up a docker container running couchdb
    #
    local IMAGE_NAME=couchdb_img
    if ! does_image_exist $IMAGE_NAME; then
        echo_to_stderr_if_not_silent "docker image '$IMAGE_NAME' does not exist"
        return 2
    fi

    local DOCKER_RUN_STDERR=$DATA_DIRECTORY/docker_run_stderr
    local KEY_STORE=$(sudo docker run \
        -d \
        --name="Key_Store" \
        -v $DATA_DIRECTORY/data:/usr/local/var/lib/couchdb \
        -v $DATA_DIRECTORY/log:/usr/local/var/log/couchdb \
        -v $DATA_DIRECTORY/run:/usr/local/var/run/couchdb \
        $IMAGE_NAME 2> "$DOCKER_RUN_STDERR")
    if [ "$KEY_STORE" == "" ]; then
        local MSG="Error starting Key Store container"
        MSG="$MSG - error details in '$DOCKER_RUN_STDERR'"
        echo_to_stderr_if_not_silent "$MSG"
        return 2
    fi

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

    local DESIGN_DOC_FILENAME="$SCRIPT_DIR_NAME/lots-of-creds/random_set_of_creds.js"
    STATUS_CODE=$(curl \
        -s \
        -o /dev/null \
        --write-out '%{http_code}' \
        -X PUT \
        -H "Content-Type: application/json; charset=utf8" \
        -d @"$DESIGN_DOC_FILENAME" \
        http://$KEY_STORE/_design/random_set_of_creds)
    if [ $? -ne 0 ] || [ "$STATUS_CODE" != "201" ]; then
        echo "-- Failed to upload design doc '$DESIGN_DOC_FILENAME' to key store @ '$KEY_STORE'"
        exit 2
    fi

    let "END = 100 - $PERCENT_OF_CREDS + 1"
    START=$(shuf -i 1-$END -n 1)
    let "END = $START + $PERCENT_OF_CREDS - 1"
    for i in $(seq $START $END)
    do
        CREDS=$(platform_safe_mktemp)

        curl -s http://$KEY_STORE/_design/random_set_of_creds/_view/all?key=$i > $CREDS

        cat $CREDS | \
            grep '^{"id"' | \
            sed -e 's/^.\+"value"://' | \
            sed -e 's/}}.\?/}/' \
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
#   1   key store
#
# exit codes
#   0   ok
#   1   general/non-specific failure - app server container not started
#   2   can't find yar_img
#
create_key_server() {

    #
    # extract function arguments and setup function specific config
    #
    local DEPLOYMENT_LOCATION=$(get_deployment_config "DEPLOYMENT_LOCATION")

    local KEY_SERVER_NUMBER=$(get_number_deployment_config_keys \
        "KEY_SERVER_CONTAINER_ID_[[:digit:]]\+")
    let "KEY_SERVER_NUMBER += 1"

    local DATA_DIRECTORY=$DEPLOYMENT_LOCATION/Key-Server-$KEY_SERVER_NUMBER
    mkdir -p $DATA_DIRECTORY

    local KEY_STORE=${1:-}

    local PORT=8070

    #
    # spin up the key sever ...
    #
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
    local DOCKER_RUN_STDERR=$DATA_DIRECTORY/docker_run_stderr
    local KEY_SERVER=$(sudo docker run \
        -d \
        --name="Key_Server_$KEY_SERVER_NUMBER" \
        -v $DATA_DIRECTORY:/var/yar_key_server \
        $IMAGE_NAME \
        $KEY_SERVER_CMD 2> "$DOCKER_RUN_STDERR")
    if [ "$KEY_SERVER" == "" ]; then
        local MSG="Error starting Key Server container"
        MSG="$MSG - error details in '$DOCKER_RUN_STDERR'"
        echo_to_stderr_if_not_silent "$MSG"
        return 2
    fi
    local KEY_SERVER_IP=$(get_container_ip $KEY_SERVER)

    echo "KEY_SERVER_CONTAINER_ID_$KEY_SERVER_NUMBER=$KEY_SERVER" >> ~/.yar.deployment
    echo "KEY_SERVER_IP_$KEY_SERVER_NUMBER=$KEY_SERVER_IP" >> ~/.yar.deployment
    echo "KEY_SERVER_END_POINT_$KEY_SERVER_NUMBER=$KEY_SERVER_IP:$PORT" >> ~/.yar.deployment

    #
    # key sever should now be running so let's verify that
    # before we return control to the caller ...
    #
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
# echo to stdout each of the key server container id keys
# listed in ~/.yar.deployment
#
# example expected usage
#
#   #!/usr/bin/env bash
#   SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#   source $SCRIPT_DIR_NAME/util.sh
#   for KSCK in $(get_all_key_server_container_id_keys); do
#       echo ">>>$KSCK<<<"
#   done
#
# arguments
#   none
#
# exit codes
#   0   ok
#   1   too many key servers in ~/.yar.deployment
#
get_all_key_server_container_id_keys() {
    for KEY_SERVER_NUMBER in {1..100}
    do
        local KEY="KEY_SERVER_CONTAINER_ID_$KEY_SERVER_NUMBER"
        local KEY_SERVER_CONTAINER_ID=$(get_deployment_config "$KEY" "")
        if [ "$KEY_SERVER_CONTAINER_ID" == "" ]; then
            return 0
        fi
        echo $KEY
    done
    return 1
}

#
# create a docker container to run the key server load balancer
#
# arguments
#   none
#
# exit codes
#   0   ok
#   1   general/non-specific failure - key server container not started
#   2   can't find haproxy_img
#
create_key_server_lb() {

    #
    # extract function arguments and setup function specific config
    #
    local DEPLOYMENT_LOCATION=$(get_deployment_config "DEPLOYMENT_LOCATION")

    local DATA_DIRECTORY=$DEPLOYMENT_LOCATION/Key-Server-LB
    mkdir -p $DATA_DIRECTORY

    local PORT=8070

    #
    # spin up the server
    #
    cp $SCRIPT_DIR_NAME/cfg-haproxy/key_server $DATA_DIRECTORY/cfg-haproxy

    local KEY_SERVER_NUMBER=1
    for KEY_SERVER_CONTAINER_ID_KEY in $(get_all_key_server_container_id_keys)
    do
        KEY_SERVER_CONTAINER_ID=$(get_deployment_config "$KEY_SERVER_CONTAINER_ID_KEY")
        KEY_SERVER_IP=$(get_container_ip "$KEY_SERVER_CONTAINER_ID")
    	echo "    server key_server_$KEY_SERVER_NUMBER $KEY_SERVER_IP check" >> $DATA_DIRECTORY/cfg-haproxy
        let "KEY_SERVER_NUMBER += 1"
    done

    local IMAGE_NAME=haproxy_img
    if ! does_image_exist $IMAGE_NAME; then
        echo_to_stderr_if_not_silent "docker image '$IMAGE_NAME' does not exist"
        return 2
    fi

    local KEY_SERVER_LB_CMD="haproxy.sh /haproxy/cfg-haproxy /haproxy/haproxy.pid"
    local DOCKER_RUN_STDERR=$DATA_DIRECTORY/docker_run_stderr
    local KEY_SERVER_LB=$(sudo docker run \
        -d \
        --name="Key_Server_LB" \
		-p $PORT:$PORT \
        -v $DATA_DIRECTORY:/haproxy \
        $IMAGE_NAME \
        $KEY_SERVER_LB_CMD 2> $DOCKER_RUN_STDERR)
    if [ "$KEY_SERVER_LB" == "" ]; then
        local MSG="Error starting Key Server LB container"
        MSG="$MSG - error details in '$DOCKER_RUN_STDERR'"
        echo_to_stderr_if_not_silent "$MSG"
        return 2
    fi
    local KEY_SERVER_LB_IP=$(get_container_ip $KEY_SERVER_LB)

    echo "KEY_SERVER_LB_CONTAINER_ID=$KEY_SERVER_LB" >> ~/.yar.deployment
    echo "KEY_SERVER_LB_IP=$KEY_SERVER_LB_IP" >> ~/.yar.deployment
    echo "KEY_SERVER_LB_END_POINT=$KEY_SERVER_LB_IP:$PORT" >> ~/.yar.deployment

    #
    # key sever lb should now be running so let's verify that
    # before we return control to the caller ...
    #
    for i in {1..10}
    do
        sleep 1
        curl -s http://$KEY_SERVER_LB_IP:$PORT/dave.html >& /dev/null
        if [ $? == 0 ]; then
            break
        fi
    done

    echo $KEY_SERVER_LB_IP:$PORT
}

#
# create a docker container to run a nonce store
#
# arguments
#   1   port on which to run the nonce store (optional, default = 11211)
#   2   MB of RAM for nonce store to use to store nonces (optional, default = 128)
#
# exit codes
#   0   ok
#   1   general/non-specific failure - nonce store container not started
#   2   can't find memcached_img
#
create_nonce_store() {

    #
    # extract function arguments and setup function specific config
    #
    local DEPLOYMENT_LOCATION=$(get_deployment_config "DEPLOYMENT_LOCATION")

    local NONCE_STORE_NUMBER=$(get_number_deployment_config_keys \
        "NONCE_STORE_CONTAINER_ID_[[:digit:]]\+")
    let "NONCE_STORE_NUMBER += 1"

    local DATA_DIRECTORY=$DEPLOYMENT_LOCATION/Nonce-Store-$NONCE_STORE_NUMBER
    mkdir -p $DATA_DIRECTORY

    local PORT=${1:-11211}

    local RAM=${2:-128}

    #
    # spin up the nonce store
    #
    local IMAGE_NAME=memcached_img
    if ! does_image_exist $IMAGE_NAME; then
        echo_to_stderr_if_not_silent "docker image '$IMAGE_NAME' does not exist"
        return 2
    fi

    local NONCE_STORE_CMD="memcached.sh \
        $PORT \
        $RAM \
        /var/nonce_store/nonce_store_log"
    local DOCKER_RUN_STDERR=$DATA_DIRECTORY/docker_run_stderr
    local NONCE_STORE=$(sudo docker run \
        -d \
        --name="Nonce_Store_$NONCE_STORE_NUMBER" \
        -v $DATA_DIRECTORY:/var/nonce_store \
        $IMAGE_NAME \
        $NONCE_STORE_CMD 2> "$DOCKER_RUN_STDERR")
    if [ "$NONCE_STORE" == "" ]; then
        local MSG="Error starting Nonce Store container"
        MSG="$MSG - error details in '$DOCKER_RUN_STDERR'"
        echo_to_stderr_if_not_silent "$MSG"
        return 2
    fi
    local NONCE_STORE_IP=$(get_container_ip $NONCE_STORE)

    echo "NONCE_STORE_CONTAINER_ID_$NONCE_STORE_NUMBER=$NONCE_STORE" >> ~/.yar.deployment
    echo "NONCE_STORE_IP_$NONCE_STORE_NUMBER=$NONCE_STORE_IP" >> ~/.yar.deployment
    echo "NONCE_STORE_END_POINT_$NONCE_STORE_NUMBER=$NONCE_STORE_IP:$PORT" >> ~/.yar.deployment

    #
    # confirm the nonce store is up and running
    #
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
# echo to stdout each of the nonce store container id keys
# listed in ~/.yar.deployment
#
# example expected usage
#
#   #!/usr/bin/env bash
#   SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#   source $SCRIPT_DIR_NAME/util.sh
#   for NSCIDK in $(get_all_nonce_store_container_id_keys); do
#       echo ">>>$NSCIDK<<<"
#   done
#
# arguments
#   none
#
# exit codes
#   0   ok
#   1   too many nonce stores in ~/.yar.deployment
#
get_all_nonce_store_container_id_keys() {
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
#   1   key server
#   2   app server
#   3   nonce store
#
# exit codes
#   0   ok
#   1   general/non-specific failure - nonce store container not started
#   2   can't find yar_img
#
create_auth_server() {

    #
    # extract function arguments and setup function specific config
    #
    local DEPLOYMENT_LOCATION=$(get_deployment_config "DEPLOYMENT_LOCATION")

    local AUTH_SERVER_NUMBER=$(get_number_deployment_config_keys \
        "AUTH_SERVER_CONTAINER_ID_[[:digit:]]\+")
    let "AUTH_SERVER_NUMBER += 1"

    local DATA_DIRECTORY=$DEPLOYMENT_LOCATION/Auth-Server-$AUTH_SERVER_NUMBER
    mkdir -p $DATA_DIRECTORY

    local KEY_SERVER=${1:-}
    local APP_SERVER=${2:-}
    local NONCE_STORE=${3:-}

    local PORT=8000

    #
    # spin up the auth server
    #
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
    local DOCKER_RUN_STDERR=$DATA_DIRECTORY/docker_run_stderr
    local AUTH_SERVER=$(sudo docker run \
        -d \
        --name="Auth_Server_$AUTH_SERVER_NUMBER" \
        -v $DATA_DIRECTORY:/var/auth_server \
        $IMAGE_NAME \
        $AUTH_SERVER_CMD 2> "$DOCKER_RUN_STDERR")
    if [ "$AUTH_SERVER" == "" ]; then
        local MSG="Error starting Auth Server container"
        MSG="$MSG - error details in '$DOCKER_RUN_STDERR'"
        echo_to_stderr_if_not_silent "$MSG"
        return 2
    fi
    local AUTH_SERVER_IP=$(get_container_ip $AUTH_SERVER)

    echo "AUTH_SERVER_CONTAINER_ID_$AUTH_SERVER_NUMBER=$AUTH_SERVER" >> ~/.yar.deployment
    echo "AUTH_SERVER_IP_$AUTH_SERVER_NUMBER=$AUTH_SERVER_IP" >> ~/.yar.deployment
    echo "AUTH_SERVER_END_POINT_$AUTH_SERVER_NUMBER=$AUTH_SERVER_IP:$PORT" >> ~/.yar.deployment

    #
    # auth server should now be running so let's verify that
    # before we return control to the caller ...
    #
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

#
# echo to stdout each of the auth server container id keys
# listed in ~/.yar.deployment
#
# example expected usage
#
#   #!/usr/bin/env bash
#   SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#   source $SCRIPT_DIR_NAME/util.sh
#   for ASIDK in $(get_all_auth_server_container_id_keys); do
#       echo ">>>$ASIDK<<<"
#   done
#
# arguments
#   none
#
# exit codes
#   0   ok
#   1   too many auth servers in ~/.yar.deployment
#
get_all_auth_server_container_id_keys() {
    for AUTH_SERVER_NUMBER in {1..100}
    do
        local KEY="AUTH_SERVER_CONTAINER_ID_$AUTH_SERVER_NUMBER"
        local AUTH_SERVER_CONTAINER_ID=$(get_deployment_config "$KEY" "")
        if [ "$AUTH_SERVER_CONTAINER_ID" == "" ]; then
            return 0
        fi
        echo $KEY
    done
    return 1
}

#
# create a docker container to run the auth server load balancer
#
# arguments
#   1   name of data directory - mkdir -p called on this name
#
# exit codes
#   0   ok
#   1   general/non-specific failure - auth server container not started
#   2   can't find haproxy_img
#
create_auth_server_lb() {

    #
    # extract function arguments and setup function specific config
    #
    local DEPLOYMENT_LOCATION=$(get_deployment_config "DEPLOYMENT_LOCATION")

    local DATA_DIRECTORY=$DEPLOYMENT_LOCATION/Auth-Server-LB
    mkdir -p $DATA_DIRECTORY

    local PORT=8000

    #
    # generate the haproxy config file
    #
    cp $SCRIPT_DIR_NAME/cfg-haproxy/auth_server $DATA_DIRECTORY/cfg-haproxy

    local AUTH_SERVER_NUMBER=1
    for AUTH_SERVER_CONTAINER_ID_KEY in $(get_all_auth_server_container_id_keys)
    do
        AUTH_SERVER_CONTAINER_ID=$(get_deployment_config "$AUTH_SERVER_CONTAINER_ID_KEY")
        AUTH_SERVER_IP=$(get_container_ip "$AUTH_SERVER_CONTAINER_ID")
    	echo "    server auth_server_$AUTH_SERVER_NUMBER $AUTH_SERVER_IP check" >> $DATA_DIRECTORY/cfg-haproxy
        let "AUTH_SERVER_NUMBER += 1"
    done

    #
    # spin up haproxy
    #
    local IMAGE_NAME=haproxy_img
    if ! does_image_exist $IMAGE_NAME; then
        echo_to_stderr_if_not_silent "docker image '$IMAGE_NAME' does not exist"
        return 2
    fi

    local AUTH_SERVER_LB_CMD="haproxy.sh /haproxy/cfg-haproxy /haproxy/haproxy.pid"
    local DOCKER_RUN_STDERR=$DATA_DIRECTORY/docker_run_stderr
    local AUTH_SERVER_LB=$(sudo docker run \
        -d \
        --name="Auth_Server_LB" \
		-p $PORT:$PORT \
        -v $DATA_DIRECTORY:/haproxy \
        $IMAGE_NAME \
        $AUTH_SERVER_LB_CMD 2> "$DOCKER_RUN_STDERR")
    if [ "$AUTH_SERVER_LB" == "" ]; then
        local MSG="Error starting Auth Server LB container"
        MSG="$MSG - error details in '$DOCKER_RUN_STDERR'"
        echo_to_stderr_if_not_silent "$MSG"
        return 2
    fi
    local AUTH_SERVER_LB_IP=$(get_container_ip $AUTH_SERVER_LB)

    echo "AUTH_SERVER_LB_CONTAINER_ID=$AUTH_SERVER_LB" >> ~/.yar.deployment
    echo "AUTH_SERVER_LB_IP=$AUTH_SERVER_LB_IP" >> ~/.yar.deployment
    echo "AUTH_SERVER_LB_END_POINT=$AUTH_SERVER_LB_IP:$PORT" >> ~/.yar.deployment

    #
    # auth server LB should now be running so let's verify that
    # before we return control to the caller ...
    #
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
    # /vagrant/cfg-collectd/collectd.conf.postfix
    # so a change in /vagrant/cfg-collectd/collectd.conf.postfix
    # won't be reflected in this code - should
    # only be defining this directory in one location
    sudo rm -rf /var/lib/collectd >& /dev/null

    TEMP_COLLECTD_CONF=$(platform_safe_mktemp)

    cat /vagrant/cfg-collectd/collectd.conf.prefix >> $TEMP_COLLECTD_CONF

	# NOTE - the if below will typically only fail if Docker's not been
	# instructed to use lxc
	if [ -d /sys/fs/cgroup/memory/lxc ]; then
		for PUSEDO_FILE in /sys/fs/cgroup/memory/lxc/*/memory.usage_in_bytes
		do
			CONTAINER_ID=$(echo $PUSEDO_FILE | \
				sed -e "s/^\/sys\/fs\/cgroup\/memory\/lxc\///" | \
				sed -e "s/\/memory.usage_in_bytes$//")

			cat /vagrant/cfg-collectd/collectd.conf.memory_usage | \
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

			cat /vagrant/cfg-collectd/collectd.conf.cpu_usage | \
				sed -e "s/%CONTAINER_ID%/$CONTAINER_ID/g" \
				>> $TEMP_COLLECTD_CONF
		done
	fi

    cat /vagrant/cfg-collectd/collectd.conf.postfix >> $TEMP_COLLECTD_CONF

    sudo mv $TEMP_COLLECTD_CONF /etc/collectd/collectd.conf

    sudo service collectd restart >& /dev/null
}
