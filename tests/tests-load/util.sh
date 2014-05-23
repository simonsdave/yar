# this file includes a collection of bash shell functions that
# felt generally reusable across a variety of bash shell scripts.
# the functions are introduced to the shell scripts with the
# following lines @ the top of the script assuming this file
# is in the same directory as the script.
#
#	SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#	source $SCRIPT_DIR_NAME/util.sh

#
# assuming start_collecting_metrics() and stop_collecting_metrics()
# have been used to collect metrics, calling this function is used
# to generate a graph for the memory used by a particular container.
#
# arguments
#   1   graph's title
#   2   key @ which the container's id can be found
#   3   filename into which the graph should be generated
#
# exit codes
#   0   ok
#
gen_mem_usage_graph() {

    local GRAPH_TITLE=${1:-}
    local CONTAINER_ID_KEY=${2:-}
    local GRAPH_FILENAME=${3:-}

    CONTAINER_ID=$(get_deployment_config "$CONTAINER_ID_KEY")
    if [ "$CONTAINER_ID" == "" ]; then
        echo_to_stderr_if_not_silent "No container ID found for '$CONTAINER_ID_KEY'"
        return 1
    fi

    #
    # :TRICKY: there's a tricky bit of code in the line below related to
    # the way we take the first 16 characters of CONTAINER_ID. collectd
    # only seems to use the first 60'ish characters from the container ID
    # to create the output file directory. The first 16 characters are more
    # than enough to uniquely identify the directory. The reason for the
    # * on the end of the directory name is acknowledgement of the 60'ish
    # statement & the fact that 16 characters is more than enough to identity
    # the directory.
    #
    METRICS_DIR=/var/lib/collectd/csv/vagrant-ubuntu-trusty-64/table-memory-${CONTAINER_ID:0:16}*
    if [ ! -d $METRICS_DIR ]; then
        echo_to_stderr_if_not_silent "Could not find memory metrics directory for '$CONTAINER_ID'"
        return 1
    fi

    #
    # take all collectd output files (which are all files in $METRICS_DIR
    # starting with gauge-), cat them into a single file and strip out the
    # "epoch,value" headers
    #
    OBSERVATIONS_1=$(platform_safe_mktemp)

    cat $METRICS_DIR/gauge-* | \
        grep "^[0-9]" | \
        sort --field-separator=$',' --key=1 -n \
        > $OBSERVATIONS_1

    #
    # so we've now got all the metrics in a single file order by time.
    # next step is to massage the metrics in preperation for graphing.
    #
    FIRST_TIME=$(head -1 $OBSERVATIONS_1 | sed -e "s/\,.\+$//g")

    AWK_PROG=$(platform_safe_mktemp)
    echo 'BEGIN       {FS = ","; OFS = ","}'                                >> $AWK_PROG
    echo '/^[0-9]+/   {print $1 - first_time, int(1 + $2/(1024.0*1024.0))}' >> $AWK_PROG

    OBSERVATIONS_2=$(platform_safe_mktemp)

    cat $OBSERVATIONS_1 | awk -v first_time=$FIRST_TIME -f $AWK_PROG > $OBSERVATIONS_2

    rm $AWK_PROG

    #
    # finally! let's generate a graph:-)
    #
    gnuplot \
        -e "input_filename='$OBSERVATIONS_2'" \
        -e "output_filename='$GRAPH_FILENAME'" \
        -e "title='$GRAPH_TITLE'" \
        $SCRIPT_DIR_NAME/gp.cfg/memory_usage \
        >& /dev/null
    if [ $? -ne 0 ]; then
        echo_to_stderr_if_not_silent "Error generating graph '$GRAPH_TITLE'"
    fi

    rm $OBSERVATIONS_1
    rm $OBSERVATIONS_2

    return 0
}

#
# assuming start_collecting_metrics() and stop_collecting_metrics()
# have been used to collect metrics, calling this function is used
# to generate a graph of CPU utilization a particular container.
#
# arguments
#   1   graph's title
#   2   key @ which the container's id can be found
#   3   filename into which the graph should be generated
#
# exit codes
#   0   ok
#   1   couldn't find container ID for supplied key (arg #2)
#
gen_cpu_usage_graph() {

    local GRAPH_TITLE=${1:-}
    local CONTAINER_ID_KEY=${2:-}
    local GRAPH_FILENAME=${3:-}

    CONTAINER_ID=$(get_deployment_config "$CONTAINER_ID_KEY")
    if [ "$CONTAINER_ID" == "" ]; then
        echo_to_stderr_if_not_silent "No container ID found for '$CONTAINER_ID_KEY'"
        return 1
    fi

    #
    # :TRICKY: there's a tricky bit of code in the line below related to
    # the way we take the first 16 characters of CONTAINER_ID. collectd
    # only seems to use the first 60'ish characters from the container ID
    # to create the output file directory. The first 16 characters are more
    # than enough to uniquely identify the directory. The reason for the
    # * on the end of the directory name is acknowledgement of the 60'ish
    # statement & the fact that 16 characters is more than enough to identity
    # the directory.
    #
    METRICS_DIR=/var/lib/collectd/csv/vagrant-ubuntu-trusty-64/table-cpu-${CONTAINER_ID:0:16}*
    if [ ! -d $METRICS_DIR ]; then
        echo_to_stderr_if_not_silent "Could not find cpu metrics directory for '$CONTAINER_ID'"
        return 1
    fi

    #
    # take all collectd output files (which are all files in $METRICS_DIR
    # starting with gauge-), cat them into a single file and strip out the
    # "epoch,value" headers
    #
    OBSERVATIONS_1=$(platform_safe_mktemp)

    cat $METRICS_DIR/gauge-* | \
        grep "^[0-9]" | \
        sort --field-separator=$',' --key=1 -n \
        > $OBSERVATIONS_1

    #
    # so we've now got all the metrics in a single file order by time.
    # next step is to massage the metrics in preperation for graphing.
    #
    FIRST_TIME=$(head -1 $OBSERVATIONS_1 | sed -e "s/\,.\+$//g")

    OBSERVATIONS_2=$(platform_safe_mktemp)

    #
    # to understand the awk script below you need to have a firm grasp
    # of what /sys/fs/cgroup/cpuacct/lxc/*/cpuacct.usage is recording.
    # here's what the manual says:
    #
    #   total CPU time (in nanoseconds) consumed by all tasks in this cgroup
    #
    # as a reminder - nanosecond = 1 / 1,000,000,000 second
    #
    AWK_PROG=$(platform_safe_mktemp)
    echo 'BEGIN     {FS = ","; OFS = ","; prev_epoch = -1;}'   >> $AWK_PROG
    echo '/^[0-9]+/ {
                        if (prev_epoch < 0)
                        {
                            prev_epoch = $1
                            prev_usage = $2
                        }
                        else
                        {
                            cpu_time_used = $2 - prev_usage
                            cpu_time_available = number_cpus * ($1 - prev_epoch) * 1000000000.0
                            cpu_percentage = 100.0 * (cpu_time_used / cpu_time_available)

                            print prev_epoch - first_time, cpu_percentage

                            prev_epoch = $1
                            prev_usage = $2
                        }
                    }' >> $AWK_PROG

    OBSERVATIONS_2=$(platform_safe_mktemp)

    local NUMBER_CPUS=$(cat /sys/fs/cgroup/cpuacct/cpuacct.usage_percpu | wc -w)

    cat $OBSERVATIONS_1 | \
        awk -v first_time=$FIRST_TIME -v number_cpus=$NUMBER_CPUS -f $AWK_PROG \
        > $OBSERVATIONS_2

    rm $AWK_PROG

    #
    # finally! let's generate a graph:-)
    #
    gnuplot \
        -e "input_filename='$OBSERVATIONS_2'" \
        -e "output_filename='$GRAPH_FILENAME'" \
        -e "title='$GRAPH_TITLE'" \
        $SCRIPT_DIR_NAME/gp.cfg/cpu_usage \
        >& /dev/null
    if [ $? -ne 0 ]; then
        echo_to_stderr_if_not_silent "Error generating graph '$GRAPH_TITLE'"
    fi

    rm $OBSERVATIONS_1
    rm $OBSERVATIONS_2

    return 0
}

#
# if locust is used as the load driver in a load tests it will output
# metrics to stdout every 2 seconds. these metrics can be parsed so we
# can graph the requests/second and # of errors. this function
# encapsulates the logic of parsing locust's output and generating
# a graph.
#
# arguments
#   1   graph's title
#   2   filename with locust's stdout
#   3   filename into which the graph should be generated
#
# exit codes
#   0   ok
#
gen_rps_and_errors_graph() {

    local GRAPH_TITLE=${1:-}
    local LOCUST_STDOUT=${2:-}
    local GRAPH_FILENAME=${3:-}

    local AWK_PROG=$(platform_safe_mktemp)

    echo 'BEGIN {
                    FS=" ";
                    OFS="\t";
                    epoch=0;
                    prev_failures=0;
                }' >> $AWK_PROG
    #
    # :TRICKY: the "+= 2" is the result of locust generating
    # metrics every 2 seconds
    #
    echo '/GET/ {
                    split($4, failures, "(");
                    print epoch, $3, failures[1] - prev_failures, $10;
                    epoch += 2;
                    prev_failures = failures[1];
                }' >> $AWK_PROG

    local RPS_AND_ERRORS_DATA=$(platform_safe_mktemp)
    awk \
        -f $AWK_PROG \
        < $LOCUST_STDOUT \
        > $RPS_AND_ERRORS_DATA

    local SCRIPT_DIR_NAME="$( cd "$( dirname "$BASH_SOURCE" )" && pwd )"
    gnuplot \
        -e "input_filename='$RPS_AND_ERRORS_DATA'" \
        -e "output_filename='$GRAPH_FILENAME'" \
        -e "title='$GRAPH_TITLE'" \
        $SCRIPT_DIR_NAME/gp.cfg/requests_per_second_and_errors \
        >& /dev/null

    rm $RPS_AND_ERRORS_DATA
    rm $AWK_PROG
}

#
# assuming start_collecting_metrics() and stop_collecting_metrics()
# have been used to collect metrics, calling this function is used
# to generate a graph of key nonce store metrics.
#
# arguments
#   1   graph's title
#   2   nonce store's IP address
#   3   filename into which the graph should be generated
#
# exit codes
#   0   ok
#
gen_nonce_store_graph() {

    local GRAPH_TITLE=${1:-}
    local IP_ADDRESS=${2:-}
    local GRAPH_FILENAME=${3:-}

	#
	# where are the memcached metrics stored?
	#
	local METRICS_DIR=/var/lib/collectd/csv/$IP_ADDRESS/memcached-nonce_store_$IP_ADDRESS
    if [ ! -d $METRICS_DIR ]; then
        echo_to_stderr_if_not_silent "Could not find memcached metrics directory for '$IP_ADDRESS'"
        return 1
    fi

    #
    # take all collectd output files, cat them into a single
	# file and strip out the "epoch,value" headers
    #
    local CACHE_HITS_1=$(platform_safe_mktemp)

    cat $METRICS_DIR/memcached_ops-hits-* | \
        grep "^[0-9]" | \
        sort --field-separator=$',' --key=1 -n \
        > $CACHE_HITS_1

    #
    # so we've now got all the metrics in a single file order by time.
    # next step is to massage the metrics in preperation for graphing.
    #
    local FIRST_TIME=$(head -1 $CACHE_HITS_1 | sed -e "s/\,.\+$//g")

    local AWK_PROG=$(platform_safe_mktemp)
    echo 'BEGIN       {FS = ","; OFS = ","}'       >> $AWK_PROG
    echo '/^[0-9]+/   {print $1 - first_time, $2}' >> $AWK_PROG

    local CACHE_HITS=$(platform_safe_mktemp)

    cat $CACHE_HITS_1 | awk -v first_time=$FIRST_TIME -f $AWK_PROG > $CACHE_HITS

    rm $AWK_PROG
    rm $CACHE_HITS_1

    #
    # take all collectd output files, cat them into a single
	# file and strip out the "epoch,value" headers
    #
    local SETS_1=$(platform_safe_mktemp)

    cat $METRICS_DIR/memcached_command-set-* | \
        grep "^[0-9]" | \
        sort --field-separator=$',' --key=1 -n \
        > $SETS_1

    #
    # so we've now got all the metrics in a single file order by time.
    # next step is to massage the metrics in preperation for graphing.
    #
    local AWK_PROG=$(platform_safe_mktemp)
    echo 'BEGIN     {
						FS = ",";
						OFS = ",";
						first_epoch = -1;
					}'   >> $AWK_PROG
    echo '/^[0-9]+/ {
                        if (first_epoch < 0)
                        {
                            first_epoch = $1
                            prev_sets = $2
                        }
                        else
                        {
                            sets = $2 - prev_sets
                            print $1 - first_epoch, sets
                            prev_sets = $2
                        }
                    }' >> $AWK_PROG

    local SETS=$(platform_safe_mktemp)

    cat $SETS_1 | awk -f $AWK_PROG > $SETS

    rm $AWK_PROG
    rm $SETS_1

    #
    # finally! let's generate a graph:-)
    #
    gnuplot \
        -e "cache_hits_input_filename='$CACHE_HITS'" \
        -e "sets_input_filename='$SETS'" \
        -e "output_filename='$GRAPH_FILENAME'" \
        -e "title='$GRAPH_TITLE'" \
        $SCRIPT_DIR_NAME/gp.cfg/nonce_store_key_metrics \
        >& /dev/null
    if [ $? -ne 0 ]; then
        echo_to_stderr_if_not_silent "Error generating graph '$GRAPH_TITLE'"
    fi

	#
	# cleanup after ourselves before returning
	#
	rm $SETS
	rm $CACHE_HITS

	#
	# done and all good:-)
	#
	return 0

}
