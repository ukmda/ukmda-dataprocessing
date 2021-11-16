#!/bin/bash

#
# Creates a report for each currently active shower in a particular year
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1
source ~/venvs/$RMS_ENV/bin/activate

export PYTHONPATH=$RMS_LOC:$PYLIB

if [ $# -eq 0 ]; then
    yr=$(date +%Y)
else
    yr=$1
fi

logger -s -t reportYear "get list of active showers"
python $PYLIB/utils/getActiveShowers.py | while read i 
do 
    logger -s -t reportYear "processing $i for $yr"
    $SRC/analysis/showerReport.sh $i $yr force
done
logger -s -t reportYear "Finished"