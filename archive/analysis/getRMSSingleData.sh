#!/bin/bash

# script to create RMS shower association details if not already present
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

source /home/ec2-user/venvs/${RMS_ENV}/bin/activate

cd $RMS_LOC
logger -s -t getRMSSingleData "starting"
indir=$MATCHDIR/RMSCorrelate
outdir=$SRC/data/tmpsingle
mkdir -p $outdir/processed > /dev/null 2>&1 

python $SRC/ukmon_pylib/converters/RMStoUKMON.py $indir $outdir

yr=$(date +%Y)
mrgfile=$DATADIR/single/singles-${yr}.csv
if [ ! -f $mrgfile ] ; then 
    echo "Ver,Y,M,D,h,m,s,Mag,Dur,Az1,Alt1,Az2,Alt2,Ra1,Dec1,Ra2,Dec2,ID,Long,Lat,Alt,Tz,AngVel,Shwr,Filename,Dtstamp" > $mrgfile
fi 
ls -1 $outdir/*.csv | while read i
do
    sed '1d' $i >> $mrgfile
    mv $i $outdir/processed
done 

logger -s -t getRMSSingleData "finished"