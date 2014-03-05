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
	
create_basic_api_key() {
	local HOST=${1:-}
	local DB=${2:-}
	
	local API_KEY=$(python -c "from yar.util.basic import APIKey; print APIKey.generate()")
	local CREDS="{\"principal\": \"dave@example.com\", \"type\": \"creds_v1.0\", \"is_deleted\": false, \"basic\": {\"api_key\": \"$API_KEY\"}}"
	local CONTENT_TYPE="Content-Type: application/json; charset=utf8"
	curl \
		-s \
		-X PUT \
		-H "$CONTENT_TYPE" \
		-d "$CREDS" \
		http://$HOST/$DB/$API_KEY \
		>& /dev/null
	if [ "$?" == "0" ]; then
		echo "$API_KEY"
	else
		echo ""
	fi
}

delete_basic_api_key() {
	local HOST=${1:-}
	local DB=${2:-}
	local API_KEY=${3:-}

	CREDS=$(curl -s http://$HOST/$DB/$API_KEY | sed 's/"is_deleted":false/"is_deleted":true/g')
	CONTENT_TYPE="Content-Type: application/json; charset=utf8"
	curl \
		-X PUT \
		-H "$CONTENT_TYPE" \
		-d "$CREDS" \
		http://$HOST/$DB/$API_KEY \
		>& /dev/null
}

fire_replication() {
	local HOST=${1:-}
	local DB1=${2:-}
	local DB2=${3:-}
	
	curl \
		-X POST \
		-H "Content-Type: application/json" \
		-d "{\"source\": \"$DB1\", \"target\": \"$DB2\"}" \
		http://$HOST/_replicate \
		>& /dev/null

	curl \
		-X POST \
		-H "Content-Type: application/json" \
		-d "{\"source\": \"$DB2\", \"target\": \"$DB1\"}" \
		http://$HOST/_replicate \
		>& /dev/null
}

configure_continuous_replication() {
	local HOST=${1:-}
	local SOURCE_DB=${2:-}
	local TARGET_DB=${3:-}
	
	curl \
		-X POST \
		-H "Content-Type: application/json" \
		-d "{\"source\": \"$SOURCE_DB\", \"target\": \"$TARGET_DB\", \"continuous\": true}" \
		http://$HOST/_replicate \
		>& /dev/null
}

HOST=127.0.0.1:5984
DB1=dave001
DB2=dave002

# create the two databases
create_database $HOST $DB1
create_database $HOST $DB2

for i in {1..1000}
    do
		create_basic_api_key $HOST $DB1 > /dev/null
    done

exit 0

API_KEY=$(create_basic_api_key $HOST $DB1)
# curl -s http://$HOST/$DB1/$API_KEY | jpp

fire_replication $HOST $DB1 $DB2

delete_basic_api_key $HOST $DB1 $API_KEY
delete_basic_api_key $HOST $DB2 $API_KEY

fire_replication $HOST $DB1 $DB2

curl -s http://$HOST/$DB1/$API_KEY | jpp
curl -s http://$HOST/$DB2/$API_KEY | jpp

exit 0
