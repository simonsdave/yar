#!/bin/bash

create_database() {
	local HOST=${1:-}
	local DB=${2:-}
	key_store_installer \
		--host=$HOST \
		--database=$DB \
		--create=true \
		--delete=true
	echo "Created database '$HOST/$DB'"
}
	
create_basic_creds() {
	local HOST=${1:-}
	local DB=${2:-}
	
	local API_KEY=$(python -c "from yar.util.basic import APIKey; print APIKey.generate()")
	local WHEN_CREATED=$(date -u)
	local CREDS="{\"principal\": \"dave@example.com\", \"type\": \"creds_v1.0\", \"is_deleted\": false, \"basic\": {\"api_key\": \"$API_KEY\"}, \"when_created\": \"$WHEN_CREATED\"}"
	local CONTENT_TYPE="Content-Type: application/json; charset=utf8"
	STATUS_CODE=$(curl \
		-s \
		-o /dev/null \
		--write-out '%{http_code}' \
		-X POST \
		-H "$CONTENT_TYPE" \
		-d "$CREDS" \
		http://$HOST/$DB)
	if [ $? -eq 0 ] && [ "$STATUS_CODE" == "201" ]; then
		echo "$API_KEY"
	else
		echo ""
	fi
}

get_basic_creds() {

	local SILENT=0
	if [ "${1:-}" == "-s" ]; then
		SILENT=1		
		shift
	fi

	local HOST=${1:-}
	local DB=${2:-}
	local API_KEY=${3:-}
	
	if [ $SILENT -ne 1 ]; then
		echo "Getting basic creds with api key '$API_KEY' from $HOST/$DB"
	fi

	local URL="http://$HOST/$DB/_design/by_identifier/_view/by_identifier?key=\"$API_KEY\""
	local APP='import sys, json; print json.dumps(json.load(sys.stdin)["rows"][0]["value"])'
	curl -s $URL | python -c "$APP"
}

delete_basic_creds() {
	local HOST=${1:-}
	local DB=${2:-}
	local API_KEY=${3:-}

	echo "Deleting basic creds with api key '$API_KEY' from $HOST/$DB"

	local TIMESTAMP=$(date "+%s")
	local CREDS=$(get_basic_creds -s $HOST $DB $API_KEY |
		sed "s/\"is_deleted\":false/\"is_deleted\":$TIMESTAMP/g")

	local APP='import sys, json; print json.load(sys.stdin)["_id"]'
	local ID=$(echo "$CREDS" | python -c "$APP")

	CONTENT_TYPE="Content-Type: application/json; charset=utf8"
	curl \
		-s \
		-o /dev/null \
		-X PUT \
		-H "$CONTENT_TYPE" \
		-d "$CREDS" \
		http://$HOST/$DB/$ID
}

fire_replication() {
	local HOST=${1:-}
	local DB1=${2:-}
	local DB2=${3:-}
	
	STATUS_CODE=$(curl \
		-s \
		-o /dev/null \
		--write-out '%{http_code}' \
		-X POST \
		-H "Content-Type: application/json" \
		-d "{\"source\": \"$DB1\", \"target\": \"$DB2\"}" \
		http://$HOST/_replicate)
	if [ $? -ne 0 ] || [ "$STATUS_CODE" -ne "200" ]; then
		echo "Error replicating from '$DB1' to '$DB2'"
		exit 1
	fi

	STATUS_CODE=$(curl \
		-s \
		-o /dev/null \
		--write-out '%{http_code}' \
		-X POST \
		-H "Content-Type: application/json" \
		-d "{\"source\": \"$DB2\", \"target\": \"$DB1\"}" \
		http://$HOST/_replicate)
	if [ $? -ne 0 ] || [ "$STATUS_CODE" -ne "200" ]; then
		echo "Error replicating from '$DB2' to '$DB1'"
		exit 1
	fi
}

configure_continuous_replication() {
	local HOST=${1:-}
	local SOURCE_DB=${2:-}
	local TARGET_DB=${3:-}
	
	curl \
		-s \
		-o /dev/null \
		-X POST \
		-H "Content-Type: application/json" \
		-d "{\"source\": \"$SOURCE_DB\", \"target\": \"$TARGET_DB\", \"continuous\": true}" \
		http://$HOST/_replicate
}

HOST=127.0.0.1:5984
DB1=dave001
DB2=dave002

# create two databases
create_database $HOST $DB1
create_database $HOST $DB2

echo "Creating Basic Auth API Key in $HOST/$DB1"
API_KEY=$(create_basic_creds $HOST $DB1)

fire_replication $HOST $DB1 $DB2

delete_basic_creds $HOST $DB1 $API_KEY
sleep 1
delete_basic_creds $HOST $DB2 $API_KEY

fire_replication $HOST $DB1 $DB2

get_basic_creds $HOST $DB1 $API_KEY
get_basic_creds $HOST $DB2 $API_KEY

exit 0
