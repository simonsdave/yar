# this file includes a collection of bash shell functions that
# felt generally reusable across a variety of bash shell scripts.
# the functions are introduced to the shell scripts with the
# following lines @ the top of the script
#
#	SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#	source $SOURCE_DIR_NAME/util.sh

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

get_from_json() {
    PATTERN=${1:-}
    JSON.sh | \
        grep $PATTERN |
        sed -e "s/$PATTERN//" |
        sed -e "s/[[:space:]]//g" |
        sed -e "s/\"//g"
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
