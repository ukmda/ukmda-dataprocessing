#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

traj=$1
ymd=${traj:0:8}

python -c "from maintenance.manageTraj import deleteDuplicate as dd; dd('$traj'); "
if [ $? == 0 ] ; then 
    $SRC/website/createOrbitIndex.sh $ymd

    # update the daily report files
    repfiles=$(grep $traj $DATADIR/dailyreports/*.txt| awk -F: '{ print $1 }')
    for repfile in $repfiles ; do
        cp $repfile $repfile.$$ 
        cat $repfile  | grep -v $traj > /tmp/newrep.txt
        mv -f /tmp/newrep.txt $repfile
    done 
    $SRC/website/publishDailyReport.sh
fi