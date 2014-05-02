#!/usr/bin/env bash
#
# yar.sh is a cli for manage a yar test deployment
# the cli lets you perform operations such as add
# and remove a server from a tier in a test deployment.
#
# exit codes
#   0           ok
#   non-zero    error
#

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
source $SCRIPT_DIR_NAME/util.sh

usage_summary() {
    echo "usage: `basename $0` [as] ..."
}

usage_detail() {
    usage_summary
    echo ""
    echo "The most commonly used `basename $0` commands are:"
    echo "  as  manage and query app servers"
}

app_server_add() {
    if [ $# != 0 ]; then
        echo "usage: `basename $0` as add"
        return 1
    fi
    create_app_server
    create_app_server_lb
    return 0
}

app_server_remove() {
    if [ $# != 1 ]; then
        echo "usage: `basename $0` as rm <app server>"
        return 1
    fi
    # from http://www.serverphorums.com/read.php?10,588090,590171#msg-590171
    # gracefully stop accepting requests & remove server
    # to 
    # set weight $SERVER 0%
    # => no new visitor is sent, wait a few minutes
    # disable server $SERVER
    # => no new connection is sent, wait a few seconds for established ones
    # to complete
    # shutdown sessions $SERVER
    # => kill all possibly remaining connections to that server
    # to bring server back online
    # set weight $SERVER 100%
    # enable server $SERVER
    return 0
}

app_server_stats() {
    if [ $# != 0 ]; then
        echo "usage: `basename $0` as stats"
        return 1
    fi
    get_app_server_stats
    return 0
}

app_server_usage() {
    echo "usage: `basename $0` as [add|rm|stats]"
}

app_server() {
    COMMAND=`echo ${1:-} | awk '{print toupper($0)}'`
    shift
    case "$COMMAND" in
        ADD)
            app_server_add $@
            ;;
        REMOVE|RM)
            app_server_remove $@
            ;;
        STATS|STAT)
            app_server_stats $@
            ;;
        "")
            app_server_usage
            return 1
            ;;
        *)
            app_server_usage
            return 1
            ;;
    esac

    return 0
}

COMMAND=`echo ${1:-} | awk '{print toupper($0)}'`
shift
case "$COMMAND" in
    AS|APP_SERVER|APP_SERVER|APPS)
        app_server $@
        ;;
    "")
        usage_detail
        exit 1
        ;;
    *)
        usage_summary
        exit 1
        ;;
esac

exit 0
