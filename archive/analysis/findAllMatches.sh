#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# Script to find correlated events, solve for their trajectories and orbits,
# then copy the results to the Archive website. 
# Parameters:
#   optional start and end days back to process. 
#   If not supplied, the environment variables MATCHSTART and MATCHEND are used
#
# Consumes:
#   All UFO and RMS single-station data (ftpdetect, platepars_all and A.xml files)
#
# Produces:
#   new and updated orbit solutions 
#   csv and extracsv files in $DATADIR/orbits/yyyy/csv and extracsv
#   daily report of matches and statistics, in $DATADIR/dailyreports
#   an email sent out via a lambda fn
#   updated orbit page, monthly and annual indexes for the website

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration and website keys
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

# logstream name inherited from parent environment but set it if not
if [ "$NJLOGSTREAM" == "" ]; then
    NJLOGSTREAM=$(date +%Y%m%d-%H%M%S)
    aws logs create-log-stream --log-group-name $NJLOGGRP --log-stream-name $NJLOGSTREAM --profile ukmonshared
fi
log2cw $NJLOGGRP $NJLOGSTREAM "start findAllMatches" findAllMatches
rundate=$(cat $DATADIR/rundate.txt)

# read start/end dates from commandline if rerunning for historical date
if [ $# -gt 0 ] ; then
    if [ "$1" != "" ] ; then
        echo "selecting range"
        MATCHSTART=$1
    fi
    if [ "$2" != "" ] ; then
        MATCHEND=$2
    else
        echo "matchend was not supplied, using 2"
        MATCHEND=$(( $MATCHSTART - 2 ))
    fi
    rundate=$(date --date="-$MATCHEND days" '+%Y%m%d')
fi

# folder for logs
mkdir -p $SRC/logs > /dev/null 2>&1

log2cw $NJLOGGRP $NJLOGSTREAM "start getRMSSingleData" findAllMatches
# this creates the parquet table for Athena
$SRC/analysis/getRMSSingleData.sh

log2cw $NJLOGGRP $NJLOGSTREAM "start createSearchable pass 1" findAllMatches
yr=$(date +%Y)
$SRC/analysis/createSearchable.sh $yr singles

startdt=$(date --date="-$MATCHSTART days" '+%Y%m%d-080000')
enddt=$(date --date="-$MATCHEND days" '+%Y%m%d-080000')
log2cw $NJLOGGRP $NJLOGSTREAM "solving for ${startdt} to ${enddt}" findAllMatches

log2cw $NJLOGGRP $NJLOGSTREAM "start runDistrib" findAllMatches
$SRC/analysis/runDistrib.sh $MATCHSTART $MATCHEND

log2cw $NJLOGGRP $NJLOGSTREAM "start checkForFailures" findAllMatches
success=$(grep "Total run time:" $SRC/logs/matchJob.log)

if [ "$success" == "" ]
then
    python -c "from meteortools.utils import sendAnEmail ; sendAnEmail('markmcintyre99@googlemail.com','problem with matching','Error in UKMON matching', mailfrom='ukmonhelper@ukmeteors.co.uk')"
    echo problems with solver
fi
log2cw $NJLOGGRP $NJLOGSTREAM "Solving Run Done" findAllMatches

log2cw $NJLOGGRP $NJLOGSTREAM "start rerunFailedLambdas" findAllMatches
python -m maintenance.rerunFailedLambdas

cd $here
log2cw $NJLOGGRP $NJLOGSTREAM "start reportOfLatestMatches" findAllMatches
python -m reports.reportOfLatestMatches $DATADIR/distrib $DATADIR $MATCHEND $rundate processed_trajectories.json

log2cw $NJLOGGRP $NJLOGSTREAM "start getMatchStats" findAllMatches
dailyrep=$(ls -1tr $DATADIR/dailyreports/20* | tail -1)
trajlist=$(cat $dailyrep | awk -F, '{print $2}')

matchlog=${SRC}/logs/matchJob.log
vals=$(python -m metrics.getMatchStats $matchlog )
evts=$(echo $vals | awk '{print $2}')
trajs=$(echo $vals | awk '{print $6}')
matches=$(wc -l $dailyrep | awk '{print $1}')
rtim=$(echo $vals | awk '{print $7}')
echo $(basename $dailyrep) $evts $trajs $matches $rtim >>  $DATADIR/dailyreports/stats.txt

# copy stats to S3 so the daily report can run
if [ "$RUNTIME_ENV" == "PROD" ] ; then 
    aws s3 sync $DATADIR/dailyreports/ $UKMONSHAREDBUCKET/matches/RMSCorrelate/dailyreports/ --quiet
fi 

log2cw $NJLOGGRP $NJLOGSTREAM "start updateIndexPages" findAllMatches
$SRC/website/updateIndexPages.sh $dailyrep

log2cw $NJLOGGRP $NJLOGSTREAM "start purgeLogs" findAllMatches
find $SRC/logs -name "matches*" -mtime +7 -exec gzip {} \;
find $SRC/logs -name "matches*" -mtime +30 -exec rm -f {} \;

log2cw $NJLOGGRP $NJLOGSTREAM "finished findAllMatches" findAllMatches
