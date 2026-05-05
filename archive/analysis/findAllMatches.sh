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

logger -s -t findAllMatches "starting"

[ -f $DATADIR/rundate.txt ] && rundate=$(cat $DATADIR/rundate.txt) || rundate=$(date +%Y%m%d)

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
mkdir -p $SRC/logs/distrib > /dev/null 2>&1

startdt=$(date --date="-$MATCHSTART days" '+%Y%m%d-080000')
enddt=$(date --date="-$MATCHEND days" '+%Y%m%d-080000')

logger -s -t findAllMatches "solving for ${startdt} to ${enddt}"
logger -s -t findAllMatches "start runDistrib"

$SRC/analysis/runDistrib.sh $MATCHSTART $MATCHEND
$SRC/utils/cleanupDeletedTrajs.sh

logger -s -t findAllMatches "Solving Run Done" 

success=$(grep "Total run time:" $SRC/logs/matchJob.log)

if [ "$success" == "" ]
then
    python -c "from utils.sendAnEmail import sendAnEmail ; sendAnEmail('markmcintyre99@googlemail.com','problem with matching','Error in UKMON matching', mailfrom='ukmonhelper@ukmeteors.co.uk')"
    echo problems with solver
fi

python -m maintenance.rerunFailedLambdas

cd $here

logger -s -t findAllMatches "start reportOfLatestMatches" 

matchlog=${SRC}/logs/matchJob.log
python -m reports.reportOfLatestMatches $DATADIR/latest/contdbs $DATADIR/dailyreports $rundate
python -m metrics.getMatchStats $matchlog $rundate

# copy stats to S3 so the daily report can run
if [ "$RUNTIME_ENV" == "PROD" ] ; then 
    aws s3 sync $DATADIR/dailyreports/ $UKMONSHAREDBUCKET/matches/RMSCorrelate/dailyreports/ --quiet
fi 

find $SRC/logs -name "matches*" -mtime +7 -exec gzip {} \;
find $SRC/logs -name "matches*" -mtime +30 -exec rm -f {} \;

logger -s -t findAllMatches "finished"
