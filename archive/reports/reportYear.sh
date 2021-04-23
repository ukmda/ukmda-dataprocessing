#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1
source ~/venvs/$RMS_ENV/bin/activate

export PYTHONPATH=$RMS_LOC:$PYLIB

if [ $# -eq 0 ]; then
    yr=$(date +%Y)
else
    yr=$1
fi

# get list of active showers
python $PYLIB/utils/getActiveShowers.py | while read i 
do 
    echo "processing $i for $yr"
    $SRC/analysis/createReport.sh $i $yr force
done
