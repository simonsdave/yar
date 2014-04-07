#!/usr/bin/env bash

# /sys/fs/cgroup/cpuacct/lxc/00abfd6674a9afa0349bcdba831c12783d71bbfa6c0306b4c141a3c9f4f4cd71/cpuacct.usage
#	the total CPU time (in nanoseconds) consumed by all tasks in this cgroup 

# Version 4 is outdated and should not be used for new setups anymore, so make sure you get a version that starts with "5.*".
# https://collectd.org/wiki/index.php/First_steps


SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
source $SCRIPT_DIR_NAME/util.sh

get_memory_used_in_bytes() {
    local CONTAINER_ID=${1:-}
    cat /sys/fs/cgroup/memory/lxc/$CONTAINER_ID/memory.usage_in_bytes
}

get_memory_used_in_kbytes() {
    local CONTAINER_ID=${1:-}
    local BYTES=$(get_memory_used_in_bytes $CONTAINER_ID)
    python -c "print int(round($BYTES / 1024.0))"
}

get_memory_used_in_megs() {
    local CONTAINER_ID=${1:-}
    local BYTES=$(get_memory_used_in_bytes $CONTAINER_ID)
    python -c "print int(round($BYTES / (1024.0 * 1024.0)))"
}

AUTH_SERVER_LB_CONTAINER_ID=$(get_deployment_config "AUTH_SERVER_LB_CONTAINER_ID")
AUTH_SERVER_CONTAINER_ID=$(get_deployment_config "AUTH_SERVER_CONTAINER_ID")
KEY_SERVER_CONTAINER_ID=$(get_deployment_config "KEY_SERVER_CONTAINER_ID")
KEY_STORE_CONTAINER_ID=$(get_deployment_config "KEY_STORE_CONTAINER_ID")
APP_SERVER_LB_CONTAINER_ID=$(get_deployment_config "APP_SERVER_LB_CONTAINER_ID")
APP_SERVER_CONTAINER_ID=$(get_deployment_config "APP_SERVER_CONTAINER_ID")

while true
do
    AUTH_SERVER_LB_MEMORY_USED_IN_MEGS=$(get_memory_used_in_megs $AUTH_SERVER_LB_CONTAINER_ID)
    AUTH_SERVER_MEMORY_USED_IN_MEGS=$(get_memory_used_in_megs $AUTH_SERVER_CONTAINER_ID)
    KEY_SERVER_MEMORY_USED_IN_MEGS=$(get_memory_used_in_megs $AUTH_SERVER_CONTAINER_ID)
    KEY_STORE_MEMORY_USED_IN_MEGS=$(get_memory_used_in_megs $KEY_STORE_CONTAINER_ID)
    APP_SERVER_LB_MEMORY_USED_IN_MEGS=$(get_memory_used_in_megs $APP_SERVER_LB_CONTAINER_ID)
    APP_SERVER_MEMORY_USED_IN_MEGS=$(get_memory_used_in_megs $APP_SERVER_CONTAINER_ID)

    echo -e "$AUTH_SERVER_LB_MEMORY_USED_IN_MEGS\t$AUTH_SERVER_MEMORY_USED_IN_MEGS\t$KEY_SERVER_MEMORY_USED_IN_MEGS\t$KEY_STORE_MEMORY_USED_IN_MEGS\t$APP_SERVER_LB_MEMORY_USED_IN_MEGS\t$APP_SERVER_MEMORY_USED_IN_MEGS"

    sleep 1
done

# echo "Auth Server LB = $AUTH_SERVER_LB_MEMORY_USED_IN_MEGS MB"
# echo "Auth Server = $AUTH_SERVER_MEMORY_USED_IN_MEGS MB"
# echo "Key Server = $KEY_SERVER_MEMORY_USED_IN_MEGS MB"
# echo "Key Store = $KEY_STORE_MEMORY_USED_IN_MEGS MB"
# echo "App Server LB = $APP_SERVER_LB_MEMORY_USED_IN_MEGS MB"
# echo "App Server = $APP_SERVER_MEMORY_USED_IN_MEGS MB"
