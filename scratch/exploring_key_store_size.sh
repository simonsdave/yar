#!/usr/bin/env bash

# | python -mjson.tool

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
source $SCRIPT_DIR_NAME/util.sh

as_mb() {
    BYTES=$1
    let "MB=$BYTES/(1024*1024)"
    echo $MB
}

database_metrics() {

    TEMP_DATABASE_METRICS=$(platform_safe_mktemp)

    curl \
        -s \
        -X GET \
        http://$1 >& $TEMP_DATABASE_METRICS

    DOC_COUNT=$(cat $TEMP_DATABASE_METRICS | get_from_json '\["doc_count"\]')
    DATA_SIZE=$(cat $TEMP_DATABASE_METRICS | get_from_json '\["data_size"\]')
    DISK_SIZE=$(cat $TEMP_DATABASE_METRICS | get_from_json '\["disk_size"\]')

    rm $TEMP_DATABASE_METRICS

    echo "database metrics ------------------------------------------------"
    echo "# docs = $DOC_COUNT"
    echo "data size = $(as_mb $DATA_SIZE) MB"
    echo "disk size = $(as_mb $DISK_SIZE) MB"

    return 0
}

creds_view_metrics() {

    TEMP_DATABASE_METRICS=$(platform_safe_mktemp)

    curl \
        -s \
        -X GET \
        http://$1/_design/creds/_info >& $TEMP_DATABASE_METRICS

    DATA_SIZE=$(cat $TEMP_DATABASE_METRICS | get_from_json '\["view_index","data_size"\]')
    DISK_SIZE=$(cat $TEMP_DATABASE_METRICS | get_from_json '\["view_index","disk_size"\]')

    rm $TEMP_DATABASE_METRICS

    echo "view metrics ----------------------------------------------------"
    echo "data size = $(as_mb $DATA_SIZE) MB"
    echo "disk size = $(as_mb $DISK_SIZE) MB"

    return 0
}

is_creds_view_compaction_running() {

    TEMP_DATABASE_METRICS=$(platform_safe_mktemp)

    curl \
        -s \
        -X GET \
        http://$1/_design/creds/_info >& $TEMP_DATABASE_METRICS

    COMPACT_RUNNING=$(cat $TEMP_DATABASE_METRICS | get_from_json '\["view_index","compact_running"\]')

    rm $TEMP_DATABASE_METRICS

    if [ "$COMPACT_RUNNING" == "true" ]; then
        return 0
    fi

    return 1
}

yar_init_deployment

KS=$(create_key_store 100000 90)
echo $KS

database_metrics "$KS"
creds_view_metrics "$KS"

echo "materializing creds view ----------------------------------------"
date
curl -s -o /dev/null "http://$KS/_design/creds/_view/by_principal?key=\"dave@example.com\""
date

database_metrics "$KS"
creds_view_metrics "$KS"

echo "compacting creds view -------------------------------------------"
curl -s -o /dev/null -H "Content-Type: application/json" -X POST http://$KS/_compact/creds

sleep 1
while is_creds_view_compaction_running "$KS"
do
    echo -n "."
    sleep 1
done
echo ""

database_metrics "$KS"
creds_view_metrics "$KS"

exit 0
