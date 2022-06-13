#!/bin/bash

# script to create single-station file for all RMS data
#
# Parameters
#   none
#
# Consumes
#   all RMS format ftpdetect and platepars_all files
#
# Produces
#   a consolidated list of single-station detections in $DATADIR/single
#   Note: this uses a proprietary format extending both RMS and UFO

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1
source $HOME/venvs/${RMS_ENV}/bin/activate

cd $RMS_LOC
logger -s -t getRMSSingleData "starting"
indir=$MATCHDIR/RMSCorrelate
outdir=$SRC/data/single/new
mkdir -p $outdir/processed > /dev/null 2>&1 

python -m converters.RMStoUKMON $indir $outdir

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

# push to S3 bucket for future use by AWS tools
source ~/venvs/${WMPL_ENV}/bin/activate
python -m converters.toParquet $SRC/data/single/singles-${yr}.csv
aws s3 sync $SRC/data/single/ $UKMONSHAREDBUCKET/matches/single/ --exclude "*" --include "*.csv" --quiet
aws s3 sync $SRC/data/single/ $UKMONSHAREDBUCKET/matches/singlepq/ --exclude "*" --include "*.parquet.gzip" --quiet

logger -s -t getRMSSingleData "finished"