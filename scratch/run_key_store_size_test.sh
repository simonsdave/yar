#!/usr/bin/env bash

# the intent of this script is to provide insight into how the
# key store's disk usage are affected the number of keys increases.
# this script accomplishes the above by spinning up a key store
# docker container, adding lots of keys while taking disk usage
# measurements along the way and finally plotting disk usage on
# simple chart(s)

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

source $SCRIPT_DIR_NAME/util.sh

run_load_test() {
    local NUMBER_OF_KEYS=${1:-}
    local NUMBER_OF_REQUESTS=${2:-}
    local CONCURRENCY=${3:-}
    local PERCENTILE=${4:-}

	# sort -R input | head -n 100 >output

    local LEFT_ZERO_PADDED_CONCURRENCY=$(python -c "print ('0'*10+'$CONCURRENCY')[-4:]")

    local PREFIX=$RESULTS_DIR/$LEFT_ZERO_PADDED_CONCURRENCY-$NUMBER_OF_REQUESTS

    local RESULTS_DATA=$PREFIX.tsv
    local RESULTS_DATA_PERCENTILE=$(mktemp)
    local RESULTS_PLOT="$PREFIX-1-reponse-time.png"
    local RESULTS_PLOT_BY_TIME="$PREFIX-2-response-time-by-time-in-test.png"

	TITLE="$START_TIME: Concurrency = $CONCURRENCY; Number of Requests = $NUMBER_OF_REQUESTS; ${PERCENTILE}th Percentile"
    gnuplot \
        -e "input_filename='$RESULTS_DATA_PERCENTILE'" \
        -e "output_filename='$RESULTS_PLOT_PERCENTILE'" \
        -e "title='$TITLE'" \
        $SCRIPT_DIR_NAME/response_time.gpcfg
}

# :TODO: what if either of these scripts fail?
$SCRIPT_DIR_NAME/rm_all_containers.sh
echo "Creating key store ..."
KEY_STORE=$(create_key_store)
echo $KEY_STORE

START_TIME=$(date +%Y-%m-%d-%H-%M)

RESULTS_DIR=$SCRIPT_DIR_NAME/test-results/key-store-size/$START_TIME
mkdir -p $RESULTS_DIR

{
  "docs": [
    { "_id": "awsdflasdfsadf", "foo": "bar" },
    { "_id": "cczsasdfwuhfas", "bwah": "there" },
    ...
  ]
}
for i in {1..1}
    do
		create_basic_api_key $KEY_STORE
    done

curl -s http://$KEY_STORE | get_from_json '\["disk_size"\]'

# SUMMARY_REPORT_FILENAME=$RESULTS_DIR/test-results-summary.pdf

# convert $RESULTS_DIR/*.png $SUMMARY_REPORT_FILENAME

# echo "Complete results in '$RESULTS_DIR'"
# echo "Summary report '$SUMMARY_REPORT_FILENAME'"

exit 0
