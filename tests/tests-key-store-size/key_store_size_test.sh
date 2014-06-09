#!/usr/bin/env bash

#   
# this script explores how the key store performs as the number
# of credentials increases
#
# exit status
#   0   ok
#   

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
source $SCRIPT_DIR_NAME/../util.sh

usage() {
    echo "usage: `basename $0` [--mnc <max # creds>] [--pbc <% basic creds>]"
}

# arguments
#   1   ip:port/database
#   2   design doc name
#   3   view name
#
# return value
#   0   always

materalize_and_compact_view() {

    KEY_STORE=${1:-}
    DESIGN_DOC=${2:-}
    VIEW=${3:-}

    if ! cdb_materalize_view "$KEY_STORE" "$DESIGN_DOC" "$VIEW"; then
        echo "View materialization failed"
        exit 1
    fi

    echo -n "-- Compacting $DESIGN_DOC ."

    if ! cdb_start_view_compaction "$KEY_STORE" "$DESIGN_DOC"; then
        echo "Failed to start view materialization"
        exit 1
    fi

    sleep 1
    while cdb_is_view_compaction_running "$KEY_STORE"
    do
        echo -n "."
        sleep 1
    done
    echo " done"

    return 0
}

MAX_NUMBER_OF_CREDS=5000000
PERCENT_BASIC_CREDS=90

while [[ 0 -ne $# ]]
do
    KEY="$1"
    shift
    case $KEY in
        --mnc)
            MAX_NUMBER_OF_CREDS=${1:-}
            shift
            ;;
        --pbc)
            PERCENT_BASIC_CREDS=${1:-}
            shift
            ;;
        *)
            usage
            exit 1
            ;;
    esac
done

if [ $# != 0 ]; then
    usage
    exit 1
fi

#
# Useful for debugging
#
echo_if_not_silent "Key Parameters" "yellow"
echo "-- Number of Creds = $MAX_NUMBER_OF_CREDS"
echo "-- Percent Basic Creds = $PERCENT_BASIC_CREDS%"

#
# where will the tests' results be saved?
#
START_TIME=$(date +%Y-%m-%d-%H-%M)
RESULTS_DIR=$SCRIPT_DIR_NAME/test-results/$START_TIME
mkdir -p "$RESULTS_DIR"

#
# some initialization before we start the meat of this script
#
DATA_DIRECTORY=$(platform_safe_mktemp_directory)

yar_init_deployment "$DATA_DIRECTORY" "yellow"

echo_if_not_silent "Creating Key Store" "yellow"
if ! KEY_STORE=$(create_key_store); then
    echo "Failed to create Key Store"
    exit 1
fi
echo "-- Key Store available @ 'http://$KEY_STORE'"
echo "-- Key Store data saved in '$DATA_DIRECTORY'"

#
# bulk load the newly created key store with a bunch
# credentials keeping track of various metrics during
# the loading process
#
DATABASE_METRICS=$RESULTS_DIR/key-store-size.tsv

creds_batch_sizes() {
    echo 1000
    echo 5000
    echo 19000
    for i in $(seq 10000)
    do
        echo 25000
    done
}

echo_if_not_silent "Starting Test" "yellow"
TOTAL_NUMBER_OF_CREDS=0
for CREDS_BATCH_SIZE in $(creds_batch_sizes)
do
    echo "-- Generating & uploading $CREDS_BATCH_SIZE creds"

    CREDS=$(platform_safe_mktemp $CREDS_BATCH_SIZE)
    sudo docker run yar_img bulk_gen_creds $CREDS_BATCH_SIZE $PERCENT_BASIC_CREDS > "$CREDS"

    STATUS_CODE=$(curl \
        -s \
        -o /dev/null \
        --write-out '%{http_code}' \
        -X POST \
        -H "Content-Type: application/json; charset=utf8" \
        -d @$CREDS \
        http://$KEY_STORE/_bulk_docs)
    if [ $? -ne 0 ] || [ "$STATUS_CODE" != "201" ]; then
        echo "Upload failed"
        exit 1
    fi

    #
    # force materialization of the creds view
    #
    materalize_and_compact_view "$KEY_STORE" "by_identifier" "by_identifier"
    materalize_and_compact_view "$KEY_STORE" "by_principal" "by_principal"

    #
    # local.ini for CouchDB should have been configured with
    #
    # [couchdb]
    # delayed_commits = false
    #
    # but in case not, we'll issue the request below to force
    # a flush to disk
    #
    STATUS_CODE=$(curl \
        -s \
        -o /dev/null \
        --write-out '%{http_code}' \
        -X POST \
        -H "Content-Type: application/json; charset=utf8" \
        http://$KEY_STORE/_ensure_full_commit)
    if [ $? -ne 0 ] || [ "$STATUS_CODE" != "201" ]; then
        echo "Flush to disk failed on key store '$KEY_STORE'"
        exit 1
    fi

    TEMP_DATABASE_METRICS=$(platform_safe_mktemp)

    curl \
        -s \
        -X GET \
        http://$KEY_STORE >& $TEMP_DATABASE_METRICS

    DOC_COUNT=$(cat $TEMP_DATABASE_METRICS | get_from_json '\["doc_count"\]')
    DATA_SIZE=$(cat $TEMP_DATABASE_METRICS | get_from_json '\["data_size"\]')
    DISK_SIZE=$(cat $TEMP_DATABASE_METRICS | get_from_json '\["disk_size"\]')

    curl \
        -s \
        -X GET \
        http://$KEY_STORE/_design/by_principal/_info  >& $TEMP_DATABASE_METRICS

    BY_PRINCIPAL_DATA_SIZE=$(cat $TEMP_DATABASE_METRICS | get_from_json '\["view_index","data_size"\]')
    BY_PRINCIPAL_DISK_SIZE=$(cat $TEMP_DATABASE_METRICS | get_from_json '\["view_index","disk_size"\]')

    curl \
        -s \
        -X GET \
        http://$KEY_STORE/_design/by_identifier/_info  >& $TEMP_DATABASE_METRICS

    BY_IDENTIFIER_DATA_SIZE=$(cat $TEMP_DATABASE_METRICS | get_from_json '\["view_index","data_size"\]')
    BY_IDENTIFIER_DISK_SIZE=$(cat $TEMP_DATABASE_METRICS | get_from_json '\["view_index","disk_size"\]')

    echo -e "$DOC_COUNT\t$DATA_SIZE\t$DISK_SIZE\t$BY_PRINCIPAL_DATA_SIZE\t$BY_PRINCIPAL_DISK_SIZE\t$BY_IDENTIFIER_DATA_SIZE\t$BY_IDENTIFIER_DISK_SIZE" >> $DATABASE_METRICS

    rm $TEMP_DATABASE_METRICS

    let "TOTAL_NUMBER_OF_CREDS = $TOTAL_NUMBER_OF_CREDS + $CREDS_BATCH_SIZE"
    if [ $MAX_NUMBER_OF_CREDS -le $TOTAL_NUMBER_OF_CREDS ]; then
        break
    fi

done

#
# now that we've generated all the metrics let's generate some pretty
# charts so we can figure out some results!
#

echo_if_not_silent "Generating result graphs" "yellow"

#
# generate a title page for the summary report
#
REPORT_TEXT="yar key store load test ($START_TIME)\n"
REPORT_TEXT=$REPORT_TEXT"\n"
REPORT_TEXT=$REPORT_TEXT"Number of Creds = $TOTAL_NUMBER_OF_CREDS\n"
REPORT_TEXT=$REPORT_TEXT"Percent Basic Creds = $PERCENT_BASIC_CREDS%"

convert \
    -background lightgray \
    -fill black \
    -size 3200x1800 \
    label:"$REPORT_TEXT" \
    -gravity center \
    $RESULTS_DIR/01-Title.png

#
# the raw metrics collected need to be massage a bit before
# we try to graph them (bytes -> MB & and of credentials ->
# '000 of credentials)
#
SUMMARY_DATABASE_METRICS=$(platform_safe_mktemp)

awk 'BEGIN {FS = "\t"; OFS = "\t"} ; \
    { print int($1/1000), int($2/(1024*1024)), int($3/(1024*1024)), int($4/(1024*1024)), int($5/(1024*1024)), int($4/(1024*1024)), int($5/(1024*1024)) }' \
    $DATABASE_METRICS > $SUMMARY_DATABASE_METRICS

#
# finally time to start generating some graphs!!!
#
gnuplot \
    -e "input_filename='$SUMMARY_DATABASE_METRICS'" \
    -e "output_filename='$RESULTS_DIR/02-Key-Store-Size.png'" \
    -e "xaxis_label='Number of Credentials (000s)'" \
    -e "yaxis_label='Size (MB)'" \
    $SCRIPT_DIR_NAME/key_store_size.gpcfg

rm $SUMMARY_DATABASE_METRICS

#
# generate the last (blank) page of the summary report
#
convert \
    -background lightgray \
    -fill black \
    -size 3200x1800 \
    label:"End of Report:-)" \
    -gravity center \
    $RESULTS_DIR/99-Last.png

#
# generate the summary report
#
SUMMARY_REPORT_FILENAME=$RESULTS_DIR/test-results-summary.pdf
convert $RESULTS_DIR/*.png $SUMMARY_REPORT_FILENAME

#
# all done now ... just let folks know where to find the results
#
echo "-- Complete results in '$RESULTS_DIR'"
echo "-- Summary report '$SUMMARY_REPORT_FILENAME'"

exit 0
