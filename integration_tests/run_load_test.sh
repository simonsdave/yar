#!/usr/bin/env bash

# after docker images have been built, this script spins up a yar
# deployment and runs a load test against that deployment

# :TODO: add check that docker images have been built

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

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

    local MIN_SECONDS=$(tail -n +2 $INPUT_FILENAME | awk 'BEGIN {min = 9999999999; FS = "\t"} ; { if($2 < min) {min = $2} } END { print min }')

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
        -v ms="$MIN_SECONDS" \
        'BEGIN {FS = "\t"; OFS = "\t"} ; \
        {print $1, $2 - ms, $3, $4, $5, $6; }' | \
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

    LOAD_TEST_RESULTS_DATA=$SCRIPT_DIR_NAME/load_test_results-$CONCURRENCY-$NUMBER_OF_REQUESTS.tsv
    LOAD_TEST_RESULTS_DATA_PERCENTILE=$SCRIPT_DIR_NAME/load_test_results-$CONCURRENCY-$NUMBER_OF_REQUESTS-$PERCENTILE.tsv
    LOAD_TEST_RESULTS_PLOT=$SCRIPT_DIR_NAME/load_test_results-$CONCURRENCY-$NUMBER_OF_REQUESTS.png

    ab \
        -c $CONCURRENCY \
        -n $NUMBER_OF_REQUESTS \
        -A $API_KEY: \
        -g $LOAD_TEST_RESULTS_DATA \
        http://172.17.0.7:8000/dave.html

    take_percentile_and_add_sanity_to_time \
        $PERCENTILE \
        $LOAD_TEST_RESULTS_DATA \
        $LOAD_TEST_RESULTS_DATA_PERCENTILE

    gnuplot \
        -e "input_filename='$LOAD_TEST_RESULTS_DATA_PERCENTILE'" \
        -e "output_filename='$LOAD_TEST_RESULTS_PLOT'" \
        -e "title='Concurrency = $CONCURRENCY; Number of Requests = $NUMBER_OF_REQUESTS; $PERCENTILE th Percentile'" \
        $SCRIPT_DIR_NAME/plot_load_test_results
}

# :TODO: what if either of these scripts fail?
$SCRIPT_DIR_NAME/rm_all_containers.sh
$SCRIPT_DIR_NAME/spin_up_deployment.sh

API_KEY=$(get_deployment_config "API_KEY")
# :TODO: what if API_KEY doesn't exist?

rm -f load_test_results* >& /dev/null

NUMBER_OF_REQUESTS=5000
PERCENTILE=95

run_load_test $NUMBER_OF_REQUESTS 1 $PERCENTILE
# run_load_test $NUMBER_OF_REQUESTS 5 $PERCENTILE
# run_load_test $NUMBER_OF_REQUESTS 10 $PERCENTILE
# run_load_test $NUMBER_OF_REQUESTS 25 $PERCENTILE
# run_load_test $NUMBER_OF_REQUESTS 50 $PERCENTILE
# run_load_test $NUMBER_OF_REQUESTS 75 $PERCENTILE
# run_load_test $NUMBER_OF_REQUESTS 100 $PERCENTILE

convert \
    $SCRIPT_DIR_NAME/*.png \
    $SCRIPT_DIR_NAME/load_test_results.pdf

exit 0
