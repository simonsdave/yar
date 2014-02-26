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

rm -f load_test_results.* >& /dev/null

# :TODO: what if either of these scripts fail?
$SCRIPT_DIR_NAME/rm_all_containers.sh
$SCRIPT_DIR_NAME/spin_up_deployment.sh

API_KEY=$(get_deployment_config "API_KEY")
# :TODO: what if API_KEY doesn't exist?

ab -c 1 -n 2500 -A $API_KEY: -g load_test_results.tsv http://172.17.0.7:8000/dave.html
$SCRIPT_DIR_NAME/plot_load_test_results
mv $SCRIPT_DIR_NAME/load_test_results.jpg $SCRIPT_DIR_NAME/load_test_results_1x2500.jpg

ab -c 10 -n 2500 -A $API_KEY: -g load_test_results.tsv http://172.17.0.7:8000/dave.html
$SCRIPT_DIR_NAME/plot_load_test_results
mv $SCRIPT_DIR_NAME/load_test_results.jpg $SCRIPT_DIR_NAME/load_test_results_10x2500.jpg

ab -c 100 -n 2500 -A $API_KEY: -g load_test_results.tsv http://172.17.0.7:8000/dave.html
$SCRIPT_DIR_NAME/plot_load_test_results
mv $SCRIPT_DIR_NAME/load_test_results.jpg $SCRIPT_DIR_NAME/load_test_results_100x2500.jpg

ab -c 250 -n 5000 -A $API_KEY: -g load_test_results.tsv http://172.17.0.7:8000/dave.html
$SCRIPT_DIR_NAME/plot_load_test_results
mv $SCRIPT_DIR_NAME/load_test_results.jpg $SCRIPT_DIR_NAME/load_test_results_250x5000.jpg

convert \
    $SCRIPT_DIR_NAME/load_test_results_1x2500.jpg \
    $SCRIPT_DIR_NAME/load_test_results_10x2500.jpg \
    $SCRIPT_DIR_NAME/load_test_results_100x2500.jpg \
    $SCRIPT_DIR_NAME/load_test_results_250x5000.jpg \
    $SCRIPT_DIR_NAME/load_test_results.pdf

exit 0
