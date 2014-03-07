#!/usr/bin/env bash

# after docker images have been built, this script spins up a yar
# deployment and runs a load test against that deployment

# :TODO: add check that docker images have been built

get_deployment_config() {
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

# given an input file (geneated by apache benchmark), generate
# an output file which represents the nth percentile of the
# input file based on the 5th column (request time) in the
# input file.
take_percentile_and_add_sanity_to_time() {
    local PERCENTILE=${1:-}
    local INPUT_FILENAME=${2:-}
    local OUTPUT_FILENAME=${3:-}

    local FIRST_EPOCH_TIME=$(tail -n +2 $INPUT_FILENAME | awk 'BEGIN {min = 9999999999; FS = "\t"} ; { if($2 < min) {min = $2} } END { print min }')

	NUM_LINES_IN_FILE=$(tail -n +2 $INPUT_FILENAME | wc -l)
	NUM_LINES_IN_PERCENTILE=$(python -c "print int($NUM_LINES_IN_FILE * $PERCENTILE)")

	sort \
        --field-separator=$'\t' \
        --key=5 \
        -n \
        $INPUT_FILENAME | \
    head \
        -n $NUM_LINES_IN_PERCENTILE | \
    awk \
        -v first_epoch_time="$FIRST_EPOCH_TIME" \
        'BEGIN {FS = "\t"; OFS = "\t"} ; \
        {print $1, $2 - first_epoch_time, $3, $4, $5, $6; }' | \
    sort \
        --field-separator=$'\t' \
        --key=2 \
        -n \
        > $OUTPUT_FILENAME
}

run_load_test() {
    local NUMBER_OF_REQUESTS=${1:-}
    local CONCURRENCY=${2:-}
    local PERCENTILE=${3:-}
    local RESULTS_DIR=${4:-}

    local LEFT_ZERO_PADDED_CONCURRENCY=$(left_zero_pad $CONCURRENCY 4)

    # :TODO: what if either of these scripts fail?
    $SCRIPT_DIR_NAME/rm_all_containers.sh
    local AUTH_SERVER_LB=$($SCRIPT_DIR_NAME/spin_up_deployment.sh -s)

    local API_KEY=$(get_deployment_config "API_KEY")
    # :TODO: what if API_KEY doesn't exist?

    local PREFIX=$RESULTS_DIR/$LEFT_ZERO_PADDED_CONCURRENCY-$NUMBER_OF_REQUESTS

    local RESULTS_DATA=$PREFIX.tsv
    local RESULTS_PLOT="$PREFIX-1-response-time.png"
    local RESULTS_PLOT_BY_TIME="$PREFIX-2-response-time-by-time-in-test.png"

    ab \
        -c $CONCURRENCY \
        -n $NUMBER_OF_REQUESTS \
        -A $API_KEY: \
        -g $RESULTS_DATA \
        http://$AUTH_SERVER_LB/dave.html

    #
    # ...
    #
	TITLE="$START_TIME: Concurrency = $CONCURRENCY; Number of Requests = $NUMBER_OF_REQUESTS"
    gnuplot \
        -e "input_filename='$RESULTS_DATA'" \
        -e "output_filename='$RESULTS_PLOT'" \
        -e "title='$TITLE'" \
        $SCRIPT_DIR_NAME/response_time.gpcfg

    #
    # ...
    #
    local RESULTS_DATA_PERCENTILE=$(mktemp)

    take_percentile_and_add_sanity_to_time \
        $PERCENTILE \
        $RESULTS_DATA \
        $RESULTS_DATA_PERCENTILE

	TITLE="$START_TIME: Concurrency = $CONCURRENCY; Number of Requests = $NUMBER_OF_REQUESTS; ${PERCENTILE}th Percentile"
    gnuplot \
        -e "input_filename='$RESULTS_DATA_PERCENTILE'" \
        -e "output_filename='$RESULTS_PLOT_BY_TIME'" \
        -e "title='$TITLE'" \
        $SCRIPT_DIR_NAME/response_time_by_time.gpcfg
}

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
source $SCRIPT_DIR_NAME/util.sh

START_TIME=$(date +%Y-%m-%d-%H-%M)

RESULTS_DIR=$SCRIPT_DIR_NAME/test-results/$START_TIME
mkdir -p $RESULTS_DIR

NUMBER_OF_REQUESTS=1000
PERCENTILE=95

run_load_test $NUMBER_OF_REQUESTS 1 $PERCENTILE $RESULTS_DIR
run_load_test $NUMBER_OF_REQUESTS 5 $PERCENTILE $RESULTS_DIR
run_load_test $NUMBER_OF_REQUESTS 10 $PERCENTILE $RESULTS_DIR
run_load_test $NUMBER_OF_REQUESTS 25 $PERCENTILE $RESULTS_DIR
run_load_test $NUMBER_OF_REQUESTS 50 $PERCENTILE $RESULTS_DIR
run_load_test $NUMBER_OF_REQUESTS 75 $PERCENTILE $RESULTS_DIR
run_load_test $NUMBER_OF_REQUESTS 100 $PERCENTILE $RESULTS_DIR

SUMMARY_REPORT_FILENAME=$RESULTS_DIR/test-results-summary.pdf

convert $RESULTS_DIR/*.png $SUMMARY_REPORT_FILENAME

echo "Complete results in '$RESULTS_DIR'"
echo "Summary report '$SUMMARY_REPORT_FILENAME'"

exit 0
