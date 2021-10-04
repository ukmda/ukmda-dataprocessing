#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1
source ~/venvs/$WMPL_ENV/bin/activate

if [ $# -lt 1 ] ; then
    yr=$(date +%Y)
    mth=$(date +%m)
    numreq=100
else
    yr=$1
    mth=$2
    numreq=$3
fi

cd $DATADIR
outdir=$DATADIR/videos/${yr}/${yr}${mth}
s3outdir=videos/${yr}/${yr}${mth}
mkdir -p $outdir > /dev/null 2>&1

export PYTHONPATH=$wmpl_loc:$PYLIB

tlist=$(python $PYLIB/reports/findBestMp4s.py $yr $mth $numreq)
for t in $tlist 
do 
    cp $MATCHDIR/RMSCorrelate/trajectories/$t*/*.mp4 $outdir
    gotcount=$(ls -1 $outdir/*.mp4 | wc -l)
    if [ $gotcount -gt $numreq ] ; then
        break
    fi
    echo "got $gotcount"
done

source $UKMONSHAREDKEY
aws s3 sync $outdir s3://ukmon-shared/$s3outdir 
