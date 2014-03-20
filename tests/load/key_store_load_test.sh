#!/usr/bin/env bash

# this script explores how the key store performs as the number
# of credentials increases
#
# JSON documents with a large number of previously generated
# credentials are bulk loaded into a key store with measurements
# being taken at intervals during the upload process. the
# metrics are plotted on graphs and a pdf summary report is
# generated.

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
source $SCRIPT_DIR_NAME/util.sh

#
# this script accepts a single optional command line argument
# which defines the rough number of credentials to load into
# the key store
#
if [ $# = 0 ]; then
    DESIRED_NUMBER_OF_CREDS=20000000
else
    if [ $# != 1 ]; then
        echo "usage: `basename $0` [<desired # of creds>]"
        exit 1
    else
        DESIRED_NUMBER_OF_CREDS=$1
    fi
fi

START_TIME=$(date +%Y-%m-%d-%H-%M)

RESULTS_DIR=$SCRIPT_DIR_NAME/test-results/key-store-load-test/$START_TIME
mkdir -p $RESULTS_DIR

#
# create a key store in an isolated container
#
KEY_STORE=$(create_key_store $RESULTS_DIR/couchdb)

#
# load up the newly created key store with a bunch
# of previously generated credentials keeping
# track of various metrics during the loading process
#
DATABASE_METRICS=$RESULTS_DIR/key-store-size.tsv

TOTAL_NUMBER_OF_CREDS=0
for CREDS in $SCRIPT_DIR_NAME/lots-of-creds/*.json
do
    echo "Uploading $CREDS"

    curl \
        -s \
        -X POST \
        -H "Content-Type: application/json; charset=utf8" \
        -d @$CREDS \
        http://$KEY_STORE/_bulk_docs \
        >& /dev/null

    TEMP_DATABASE_METRICS=$(mktemp 2> /dev/null || mktemp -t DAS)

    curl \
        -s \
        -X GET \
        http://$KEY_STORE >& $TEMP_DATABASE_METRICS

    DOC_COUNT=$(cat $TEMP_DATABASE_METRICS | get_from_json '\["doc_count"\]')
    DATA_SIZE=$(cat $TEMP_DATABASE_METRICS | get_from_json '\["data_size"\]')
    DISK_SIZE=$(cat $TEMP_DATABASE_METRICS | get_from_json '\["disk_size"\]')

    echo -e "$DOC_COUNT\t$DATA_SIZE\t$DISK_SIZE" >> $DATABASE_METRICS

    rm $TEMP_DATABASE_METRICS

    NUMBER_OF_CREDS=$(echo $CREDS | sed s/\\/.*\\/[[:digit:]]*-0*// | sed s/.json$//)
    TOTAL_NUMBER_OF_CREDS=$(python -c "print $TOTAL_NUMBER_OF_CREDS + int($NUMBER_OF_CREDS)")
    if [ $DESIRED_NUMBER_OF_CREDS -le $TOTAL_NUMBER_OF_CREDS ]; then
        break
    fi

done

# :TODO: tell $KEY_STORE to clean itself up

#
# now that we've generated all the metrics let's generate some pretty
# charts so we can figure out some results!
#

#
# generate a title page for the summary report
#
REPORT_TEXT="yar key store load test ($START_TIME)\n"

convert \
    -background lightgray \
    -fill black \
    -size 1280x720 \
    label:"$REPORT_TEXT" \
    -gravity center \
    $RESULTS_DIR/01-Title.png

#
# the raw metrics collected need to be massage a bit before
# we try to graph them (bytes -> MB & and of credentials ->
# '000 of credentials)
#
SUMMARY_DATABASE_METRICS=$(mktemp 2> /dev/null || mktemp -t DAS)

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
    $SCRIPT_DIR_NAME/gpcfg/key_store_size.gpcfg

rm $SUMMARY_DATABASE_METRICS

#
# generate the last (blank) page of the summary report
#
convert \
    -background lightgray \
    -fill black \
    -size 1280x720 \
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
echo "Complete results in '$RESULTS_DIR'"
echo "Summary report '$SUMMARY_REPORT_FILENAME'"

exit 0
