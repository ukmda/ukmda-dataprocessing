#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

if [ "$1" == "" ] ; then
    echo "usage: deleteOrbit.sh fulltrajname {optional jd}"
    exit 0
fi

traj=$1
ymd=${traj:0:8}

if [ "$2" == "" ]; then 
    python -c "from maintenance.manageTraj import deleteDuplicate as dd; dd('$traj'); "
else
    python -c "from maintenance.manageTraj import deleteDuplicate as dd; dd('$traj', $2); "
fi 
if [ $? == 0 ] ; then 
    $SRC/website/createOrbitIndex.sh $ymd

    # update the daily report files
    repfiles=$(grep $traj $DATADIR/dailyreports/*.txt| awk -F: '{ print $1 }')
    for repfile in $repfiles ; do
        cp $repfile $repfile.$$ 
        cat $repfile  | grep -v $traj > /tmp/newrep.txt
        mv -f /tmp/newrep.txt $repfile
    done 
fi
