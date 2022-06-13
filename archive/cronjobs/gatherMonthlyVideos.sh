#!/bin/bash
#
# Collect monthly videos for making into a youtube post
#
# Parameters
#   the month to process in yyyymm format
#
# Consumes
#   MP4s from the archive
#
# Produces
#   MP4s in $DATADIR/videos, synced to the website

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1
source ~/venvs/$WMPL_ENV/bin/activate

if [ $# -lt 1 ] ; then
    yr=$(date --date="1 week ago" +%Y)
    mth=$(date --date="1 week ago" +%m)
    numreq=100
else
    yr=$1
    mth=$2
    numreq=$3
fi
export TMP=/tmp
cd $DATADIR
outdir=$DATADIR/videos/${yr}/${yr}${mth}
s3outdir=videos/${yr}/${yr}${mth}
mkdir -p $outdir > /dev/null 2>&1

tlist=$(python -m reports.findBestMp4s $yr $mth $numreq)
for t in $tlist 
do 
    aws s3 cp $WEBSITEBUCKET/$t $outdir
done

aws s3 sync $outdir s3://ukmon-shared/$s3outdir --quiet
