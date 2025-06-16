#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1

if [ "$1" == "" ] ; then
    echo bad input 
    exit 0
fi
dt=$1
numdays=$2

basepth=~/dev/data/RMSCorrelate
mkdir -p $basepth

fldrs=$(aws s3 ls s3://ukmda-shared/matches/RMSCorrelate/ | egrep "UK|BE|IE|NL" | awk '{print $2}')

for fldr in $fldrs ; do
    for i in $(seq 1 $numdays) ; do 
        d2=$(python -c "import datetime;d1=datetime.datetime.strptime('$dt', '%Y%m%d')+datetime.timedelta(days=$i-1);print(d1.strftime('%Y%m%d'))")
        camid=${fldr:0:6}
        echo checking $camid for $d2
        aws s3 sync s3://ukmda-shared/matches/RMSCorrelate/${fldr} ${basepth}/${fldr} --exclude "*" --include "${camid}_${d2}*"    
    done
done 

for i in $(seq 1 $numdays) ; do 
    d2=$(python -c "import datetime;d1=datetime.datetime.strptime('$dt', '%Y%m%d')+datetime.timedelta(days=$i-1);print(d1.strftime('%Y%m%d'))")
    echo getting trajectories for $d2
    fldr="trajectories/${d2:0:4}/${d2:0:6}/$d2"
    aws s3 sync s3://ukmda-shared/matches/RMSCorrelate/${fldr} ${basepth}/${fldr} --exclude "*" --include "${d2}*"
done
