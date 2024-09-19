#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
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
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

logger -s -t getRMSSingleData "starting"
indir=$UKMONSHAREDBUCKET/matches/single/new/
outdir=$DATADIR/single/new
mkdir -p $outdir/processed > /dev/null 2>&1 

if [ $# -eq 0 ]; then
    yr=$(date +%Y)
else
    yr=$1
fi

aws s3 mv $indir $outdir --recursive --exclude "*" --include "ukmda_??????_${yr}*.csv" --quiet

mrgfile=$DATADIR/single/singles-${yr}.csv
newsngl=$DATADIR/single/singles-${yr}-new.csv
if [ ! -f $mrgfile ] ; then 
    cat $SRC/analysis/templates/ukmon-single.txt > $mrgfile
fi 
# file containing only new data
cat $SRC/analysis/templates/ukmon-single.txt > > $newsngl

ls -1 $outdir/ukmda_??????_${yr}*.csv | while read i
do
    cat $i >> $mrgfile
    cat $i >> $newsngl
    mv $i $outdir/processed
done 

logger -s -t getRMSSingleData "convert to parquet"
if [ -f $mrgfile ] ; then 
    python -m converters.toParquet $mrgfile
fi 
if [ -f $newsngl ] ; then 
    python -m converters.toParquet $newsngl
    \rm -f $newsngl
fi 

# push to S3 bucket for future use by AWS tools
logger -s -t getRMSSingleData "copy to S3 bucket"
aws s3 sync $SRC/data/single/ $UKMONSHAREDBUCKET/matches/single/ --exclude "*" --include "*.csv" --exclude "new/*" --quiet
aws s3 sync $SRC/data/single/ $UKMONSHAREDBUCKET/matches/singlepq/ --exclude "*" --include "*.parquet.snap" --exclude "*new.parquet.snap" --quiet

logger -s -t getRMSSingleData "finished"