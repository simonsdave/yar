# this file includes a collection of couchdb bash shell functions
# that felt generally reusable across a variety of bash shell scripts.
# the functions are introduced to the shell scripts with the
# following lines @ the top of the script assuming this file
# is in the same directory as the script.
#
#	SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
#	source $SCRIPT_DIR_NAME/couchdb_util.sh

# issue a curl request to a view for for the view
# to materialize
#
# arguments
#   1   ip:port/database
#   2   design doc name
#   3   view name
#
# return value
#   0   on success
#   1   on failure

cdb_materalize_view() {

    COUCHDB=${1:-}
    DESIGN_DOC=${2:-}
    VIEW=${3:-}

    STATUS_CODE=$(curl \
        -s \
        -o /dev/null \
        --write-out '%{http_code}' \
        http://$COUCHDB/_design/$DESIGN_DOC/_view/$VIEW?limit=1)
    if [ $? -ne 0 ] || [ "$STATUS_CODE" != "200" ]; then
        return 1
    fi

    return 0

}
