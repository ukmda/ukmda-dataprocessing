#!/bin/bash
#
# script to update match data each night and then recalc any necessary orbits

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1

logger -s -t updateSearchIndex "creating searchable indices"
$SRC/analysis/createSearchable.sh

logger -s -t updateSearchIndex "creating station list"
$SRC/website/createStationList.sh

find $SRC/logs -name "updateSearchIndex*" -mtime +7 -exec rm -f {} \;
logger -s -t updateSearchIndex "finished"