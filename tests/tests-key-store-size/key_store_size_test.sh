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

#
# this script accepts one optional (--mnc) command line argument
# which defines (roughly) the max number of credentials to load
# into the key store
#
usage() {
    echo "usage: `basename $0` [--mnc <max # creds>]"
}

MAX_NUMBER_OF_CREDS=20000000

while [[ 0 -ne $# ]]
do
    KEY="$1"
    shift
    case $KEY in
        --mnc)
            MAX_NUMBER_OF_CREDS=${1:-}
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
# where will the tests' results be saved?
#
START_TIME=$(date +%Y-%m-%d-%H-%M)
RESULTS_DIR=$SCRIPT_DIR_NAME/test-results/$START_TIME
mkdir -p "$RESULTS_DIR"

#
# some initialization before we start the meat of this script
#
DATA_DIRECTORY=$(platform_safe_mktemp_directory)

yar_init_deployment "$DATA_DIRECTORY"

echo_in_yellow "Creating Key Store"
if ! KEY_STORE=$(create_key_store); then
    echo "Failed to create Key Store"
    exit 1
fi
echo "-- Key Store available @ '$KEY_STORE'"
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
    for i in $(seq 100)
    do
        echo 25000
    done
}

echo_in_yellow "Starting Test"
TOTAL_NUMBER_OF_CREDS=0
for CREDS_BATCH_SIZE in $(creds_batch_sizes)
do
    echo "-- Generating & uploading $CREDS_BATCH_SIZE creds"

    CREDS=$(platform_safe_mktemp $CREDS_BATCH_SIZE)
    sudo docker run yar_img gen_basic_creds $CREDS_BATCH_SIZE > "$CREDS"

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

    echo -e "$DOC_COUNT\t$DATA_SIZE\t$DISK_SIZE" >> $DATABASE_METRICS

    rm $TEMP_DATABASE_METRICS

    let "TOTAL_NUMBER_OF_CREDS = $TOTAL_NUMBER_OF_CREDS + $CREDS_BATCH_SIZE"
    if [ $MAX_NUMBER_OF_CREDS -le $TOTAL_NUMBER_OF_CREDS ]; then
        break
    fi

done

# :TODO: tell $KEY_STORE to clean itself up

#
# now that we've generated all the metrics let's generate some pretty
# charts so we can figure out some results!
#

echo_in_yellow "Generating result graphs"

#
# generate a title page for the summary report
#
REPORT_TEXT="yar key store load test ($START_TIME)\n"

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
    { print int($1/1000), int($2/(1024*1024)), int($3/(1024*1024)) }' \
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
