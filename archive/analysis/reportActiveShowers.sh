#!/bin/bash
#
# Creates a report for each currently active shower in a particular year
#
# Parameters
#   the year to process in yyyy format
#
# Consumes
#   The single and matched data from $DATADIR/single and $DATADIR/matched
#   The IAU shower database in $WMPL_LOC/wmpl/share
#
# Produces
#   A report per shower with diagrams and tables, in $DATADIR/reports/yyyy
#    which is also synced to the website

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
source ~/venvs/$RMS_ENV/bin/activate
logger -s -t reportActiveShowers "starting"
$SRC/utils/clearCaches.sh

if [ $# -eq 0 ]; then
    yr=$(date +%Y)
else
    yr=$1
fi

logger -s -t reportActiveShowers "get list of active showers"
python -m utils.getActiveShowers | while read i 
do 
    logger -s -t reportActiveShowers "processing $i for $yr"
    $SRC/analysis/showerReport.sh $i $yr force
done
$SRC/utils/clearCaches.sh
logger -s -t reportActiveShowers "finished"