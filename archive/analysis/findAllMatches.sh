#!/bin/bash
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
source $here/../config/config.ini >/dev/null 2>&1
source ~/venvs/${WMPL_ENV}/bin/activate
source $UKMONSHAREDKEY

rundate=$(cat $DATADIR/rundate.txt)

# read start/end dates from commandline if rerunning for historical date
if [ $# -gt 0 ] ; then
    if [ "$1" != "" ] ; then
        echo "selecting range"
        MATCHSTART=$1
    fi
    if [ "$2" != "" ] ; then
        MATCHEND=$(( $MATCHSTART - $2 ))
    else
        echo "matchend was not supplied, using 2"
        MATCHEND=$(( $MATCHSTART - 2 ))
    fi
    rundate=$(date --date="-$MATCHEND days" '+%Y%m%d')
fi

# folder for logs
mkdir -p $SRC/logs > /dev/null 2>&1

logger -s -t findAllMatches1 "get all UFO data into the right format"
$SRC/analysis/convertUfoToRms.sh
dom=`date '+%d'`
if [ $dom -lt 10 ] ; then 
    lastmth=`date --date='-1 month' '+%Y%m'`
    $SRC/analysis/convertUfoToRms.sh $lastmth
fi
logger -s -t findAllMatches "create ukmon specific merged single-station data file"
# this creates the parquet table for Athena
$SRC/analysis/getRMSSingleData.sh

logger -s -t findAllMatches1 "set the date range for the solver"

startdt=$(date --date="-$MATCHSTART days" '+%Y%m%d-080000')
enddt=$(date --date="-$MATCHEND days" '+%Y%m%d-080000')
logger -s -t findAllMatches1 "solving for ${startdt} to ${enddt}"

logger -s -t findAllMatches1 "preserve previous trajectories database"
thisjson=$MATCHDIR/RMSCorrelate/processed_trajectories.json.bigserver
cp $thisjson $MATCHDIR/RMSCorrelate/prev_processed_trajectories.json.bigserver

logger -s -t findAllMatches1 "actually run the matching process"
$SRC/analysis/runMatching.sh $MATCHSTART $MATCHEND

logger -s -t findAllMatches2 "check if the solver had some sort of failiure"
logf=$(ls -1tr $SRC/logs/matches-*.log | tail -1)
success=$(grep "SOLVING RUN DONE" $logf)

if [ "$success" == "" ]
then
    python -m utils.sendAnEmail markmcintyre99@googlemail.com "problem with matching" "Error"
    echo problems with solver
fi
logger -s -t findAllMatches2 "Solving run done"
logger -s -t findAllMatches2 "================"

logger -s -t findAllMatches2 "waiting for lambdas to finish"
# need to wait here till the lambdas creating orbit pages are finished
sleep 600
# catchall to reprocess any failed orbit page updates
source $WEBSITEKEY
python -m utils.rerunFailedGetExtraFiles

cd $here
logger -s -t findAllMatches2 "create text file containing most recent matches"
# this compares the previous and current trajectory database (json file)
python -m reports.reportOfLatestMatches $MATCHDIR/RMSCorrelate $DATADIR $MATCHEND $rundate

logger -s -t findAllMatches2 "gather some stats"

dailyrep=$(ls -1tr $DATADIR/dailyreports/20* | tail -1)
trajlist=$(cat $dailyrep | awk -F, '{print $2}')

matchlog=$( ls -1 ${SRC}/logs/matches-*.log | tail -1)
vals=$(python -m utils.getMatchStats $matchlog )
evts=$(echo $vals | awk '{print $2}')
trajs=$(echo $vals | awk '{print $6}')
matches=$(wc -l $dailyrep | awk '{print $1}')
rtim=$(grep "Total run time" $matchlog | awk '{print $4}')
echo $(basename $dailyrep) $evts $trajs $matches $rtim >>  $DATADIR/dailyreports/stats.txt

# copy stats to S3 so the daily report can run
if [ "$RUNTIME_ENV" == "PROD" ] ; then 
    rsync -avz $DATADIR/dailyreports/ $MATCHDIR/RMSCorrelate/dailyreports/
fi 

logger -s -t findAllMatches2 "update the Index page for the month and the year"
$SRC/website/updateIndexPages.sh $dailyrep

logger -s -t findAllMatches2 "backup the solved trajectory data"
mkdir -p $DATADIR/trajdb > /dev/null 2>&1
lastjson=$(ls -1tr $DATADIR/trajdb/| grep -v ".gz" | tail -1)
thisjson=$MATCHDIR/RMSCorrelate/processed_trajectories.json.bigserver
cp $thisjson $DATADIR/trajdb/processed_trajectories.json.$(date +%Y%m%d).bigserver
gzip $DATADIR/trajdb/$lastjson

logger -s -t findAllMatches2 "purge old logs"
find $SRC/logs -name "matches*" -mtime +7 -exec gzip {} \;
find $SRC/logs -name "matches*" -mtime +30 -exec rm -f {} \;

logger -s -t findAllMatches2 "Matching process finished"