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

    local RESULTS_FILE_BASE_NAME=$RESULTS_DIR/$(left_zero_pad $CONCURRENCY 4)-$NUMBER_OF_REQUESTS

    local DOCKER_CONTAINER_DATA=$RESULTS_DIR/$(left_zero_pad $CONCURRENCY 4)-$NUMBER_OF_REQUESTS
    mkdir -p $DOCKER_CONTAINER_DATA
    # :TODO: what if this scripts fails?
    $SCRIPT_DIR_NAME/rm_all_containers.sh
    local AUTH_SERVER_LB=$($SCRIPT_DIR_NAME/spin_up_deployment.sh -s $DOCKER_CONTAINER_DATA)

    local API_KEY=$(get_deployment_config "API_KEY")
    # :TODO: what if API_KEY doesn't exist?

    local RESULTS_DATA=$RESULTS_FILE_BASE_NAME-raw-data.tsv
    ab \
        -c $CONCURRENCY \
        -n $NUMBER_OF_REQUESTS \
        -A $API_KEY: \
        -g $RESULTS_DATA \
        http://$AUTH_SERVER_LB/dave.html

    #
    # take ab's tsv output file and using gnuplot to create a
    # histogram of all response times
    #
	TITLE="Auth Server Response Time - $START_TIME: Concurrency = $CONCURRENCY; Number of Requests = $NUMBER_OF_REQUESTS"
    gnuplot \
        -e "input_filename='$RESULTS_DATA'" \
        -e "output_filename='$RESULTS_FILE_BASE_NAME-1-response-time.png'" \
        -e "title='$TITLE'" \
        $SCRIPT_DIR_NAME/response_time.gpcfg

    #
    # take a percentile of ab's tsv output file and using gnupot
    # generate a plot of response time by time in the test (look
    # at one of the output plots & this description will make more
    # sense)
    #
    local RESULTS_DATA_PERCENTILE=$(mktemp)

    take_percentile_and_add_sanity_to_time \
        $PERCENTILE \
        $RESULTS_DATA \
        $RESULTS_DATA_PERCENTILE

	TITLE="Auth Server Response Time - $START_TIME: Concurrency = $CONCURRENCY; Number of Requests = $NUMBER_OF_REQUESTS; ${PERCENTILE}th Percentile"
    gnuplot \
        -e "input_filename='$RESULTS_DATA_PERCENTILE'" \
        -e "output_filename='$RESULTS_FILE_BASE_NAME-2-response-time-by-time-in-test.png'" \
        -e "title='$TITLE'" \
        $SCRIPT_DIR_NAME/response_time_by_time.gpcfg

    #
    # during the load test the auth server was making requests
    # to the key server. the statements below extract timing
    # information about the requests from the auth server's
    # log and then plots 2 different graphs of response times.
    #
    TEMPFILE=$(mktemp)
    cat $DOCKER_CONTAINER_DATA/Auth-Server/auth_server_log | \
        grep "Key Server.*responded in [0-9]\+ ms$" | \
        awk 'BEGIN {FS = "\t"; OFS = "\t"}; { print int($1 / 1000), $5 }' | \
        sed -s "s/\tKey Server.*responded in /\t/g" |
        sed -s "s/[[:space:]]ms$//g" \
        > $TEMPFILE

	TITLE="Key Server Response Time - $START_TIME: Concurrency = $CONCURRENCY; Number of Requests = $NUMBER_OF_REQUESTS"
    gnuplot \
        -e "input_filename='$TEMPFILE'" \
        -e "output_filename='$RESULTS_FILE_BASE_NAME-3-key-server-response-time.png'" \
        -e "title='$TITLE'" \
        $SCRIPT_DIR_NAME/yar_server_response_time.gpcfg

	TITLE="Key Server Response Time - $START_TIME: Concurrency = $CONCURRENCY; Number of Requests = $NUMBER_OF_REQUESTS; ${PERCENTILE}th Percentile"
    gnuplot \
        -e "input_filename='$TEMPFILE'" \
        -e "output_filename='$RESULTS_FILE_BASE_NAME-4-key-server-response-time-by-time-in-test.png'" \
        -e "title='$TITLE'" \
        $SCRIPT_DIR_NAME/yar_server_response_time_by_time.gpcfg

    rm -f $TEMPFILE >& /dev/null

    #
    # during the load test the key server was making requests
    # to the key store. the statements below extract timing
    # information about the requests from the key server's
    # log and then plots 2 different graphs of response times.
    #
    TEMPFILE=$(mktemp)
    cat $DOCKER_CONTAINER_DATA/Key-Server/key_server_log | \
        grep "Key Store.*responded in [0-9]\+ ms$" | \
        awk 'BEGIN {FS = "\t"; OFS = "\t"}; { print int($1 / 1000), $5 }' | \
        sed -s "s/\tKey Store.*responded in /\t/g" |
        sed -s "s/[[:space:]]ms$//g" \
        > $TEMPFILE

	TITLE="Key Store Response Time - $START_TIME: Concurrency = $CONCURRENCY; Number of Requests = $NUMBER_OF_REQUESTS"
    gnuplot \
        -e "input_filename='$TEMPFILE'" \
        -e "output_filename='$RESULTS_FILE_BASE_NAME-5-key-store-response-time.png'" \
        -e "title='$TITLE'" \
        $SCRIPT_DIR_NAME/yar_server_response_time.gpcfg

	TITLE="Key Store Response Time - $START_TIME: Concurrency = $CONCURRENCY; Number of Requests = $NUMBER_OF_REQUESTS; ${PERCENTILE}th Percentile"
    gnuplot \
        -e "input_filename='$TEMPFILE'" \
        -e "output_filename='$RESULTS_FILE_BASE_NAME-6-key-store-response-time-by-time-in-test.png'" \
        -e "title='$TITLE'" \
        $SCRIPT_DIR_NAME/yar_server_response_time_by_time.gpcfg

    rm -f $TEMPFILE >& /dev/null

    #
    # during the load test the auth server was making requests
    # to the app server. the statements below extract timing
    # information about the requests from the auth server's
    # log and then plots 2 different graphs of response times.
    #
    TEMPFILE=$(mktemp)
    cat $DOCKER_CONTAINER_DATA/Auth-Server/auth_server_log | \
        grep "App Server.*responded in [0-9]\+ ms$" | \
        awk 'BEGIN {FS = "\t"; OFS = "\t"}; { print int($1 / 1000), $5 }' | \
        sed -s "s/\tApp Server.*responded in /\t/g" |
        sed -s "s/[[:space:]]ms$//g" \
        > $TEMPFILE

	TITLE="App Server Response Time - $START_TIME: Concurrency = $CONCURRENCY; Number of Requests = $NUMBER_OF_REQUESTS"
    gnuplot \
        -e "input_filename='$TEMPFILE'" \
        -e "output_filename='$RESULTS_FILE_BASE_NAME-7-app-server-response-time.png'" \
        -e "title='$TITLE'" \
        $SCRIPT_DIR_NAME/yar_server_response_time.gpcfg

	TITLE="App Server Response Time - $START_TIME: Concurrency = $CONCURRENCY; Number of Requests = $NUMBER_OF_REQUESTS; ${PERCENTILE}th Percentile"
    gnuplot \
        -e "input_filename='$TEMPFILE'" \
        -e "output_filename='$RESULTS_FILE_BASE_NAME-8-app-server-response-time-by-time-in-test.png'" \
        -e "title='$TITLE'" \
        $SCRIPT_DIR_NAME/yar_server_response_time_by_time.gpcfg

    rm -f $TEMPFILE >& /dev/null

}

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
source $SCRIPT_DIR_NAME/util.sh

START_TIME=$(date +%Y-%m-%d-%H-%M)

RESULTS_DIR=$SCRIPT_DIR_NAME/test-results/$START_TIME
mkdir -p $RESULTS_DIR

NUMBER_OF_REQUESTS=1000
PERCENTILE=95

# run_load_test $NUMBER_OF_REQUESTS 1 $PERCENTILE $RESULTS_DIR
# run_load_test $NUMBER_OF_REQUESTS 5 $PERCENTILE $RESULTS_DIR
# run_load_test $NUMBER_OF_REQUESTS 10 $PERCENTILE $RESULTS_DIR
# run_load_test $NUMBER_OF_REQUESTS 25 $PERCENTILE $RESULTS_DIR
run_load_test $NUMBER_OF_REQUESTS 50 $PERCENTILE $RESULTS_DIR
# run_load_test $NUMBER_OF_REQUESTS 75 $PERCENTILE $RESULTS_DIR
# run_load_test $NUMBER_OF_REQUESTS 100 $PERCENTILE $RESULTS_DIR

SUMMARY_REPORT_FILENAME=$RESULTS_DIR/test-results-summary.pdf

convert $RESULTS_DIR/*.png $SUMMARY_REPORT_FILENAME

echo "Complete results in '$RESULTS_DIR'"
echo "Summary report '$SUMMARY_REPORT_FILENAME'"

exit 0
