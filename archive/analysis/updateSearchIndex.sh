#!/bin/bash
#
# script to update match data each night and then recalc any necessary orbits
#
# Parameters
#   none
#
# Consumes
#   single-station, matched and live data  in $DATADIR/single, $DATADIR/matched and $DATADIR/ukmonlive
#
# Produces
#   a single searchable file in $DATADIR/searchidx
#   a list of stations that are in the search file, in a javascript form

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1

logger -s -t updateSearchIndex "creating searchable indices"
$SRC/analysis/createSearchable.sh

logger -s -t updateSearchIndex "creating station list"
$SRC/website/createStationList.sh

find $SRC/logs -name "updateSearchIndex*" -mtime +7 -exec rm -f {} \;
logger -s -t updateSearchIndex "finished"