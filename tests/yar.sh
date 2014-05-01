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
    fi
    create_app_server
    create_app_server_lb
    return 0
}

app_server_stats() {
    if [ $# != 0 ]; then
        echo "usage: `basename $0` as stats"
    fi
    get_app_server_stats
    return 0
}

app_server_usage() {
    echo "usage: `basename $0` as [add|stats]"
}

app_server() {
    COMMAND=`echo ${1:-} | awk '{print toupper($0)}'`
    shift
    case "$COMMAND" in
        ADD)
            app_server_add $@
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
