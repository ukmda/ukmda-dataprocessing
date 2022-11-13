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
logger -s -t findAllMatches "RUNTIME $SECONDS start findAllMatches"

# load the configuration and website keys
source $here/../config.ini >/dev/null 2>&1
source ~/venvs/${WMPL_ENV}/bin/activate
logger -s -t findAllMatches1 "starting"
$SRC/utils/clearCaches.sh

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

# trigger lambdas for any ftpdetects missed earlier
python -c "from utils.rerunFailedLambdas import checkMissedFTPdetect ; checkMissedFTPdetect();"

logger -s -t findAllMatches "RUNTIME $SECONDS start convertUfoToRms"
$SRC/analysis/convertUfoToRms.sh
dom=`date '+%d'`
if [ $dom -lt 10 ] ; then 
    lastmth=`date --date='-1 month' '+%Y%m'`
    $SRC/analysis/convertUfoToRms.sh $lastmth
fi
logger -s -t findAllMatches "RUNTIME $SECONDS start getRMSSingleData"
# this creates the parquet table for Athena
$SRC/analysis/getRMSSingleData.sh

logger -s -t findAllMatches "RUNTIME $SECONDS start createSearchable pass 1"
yr=$(date +%Y)
$SRC/analysis/createSearchable.sh $yr 1

startdt=$(date --date="-$MATCHSTART days" '+%Y%m%d-080000')
enddt=$(date --date="-$MATCHEND days" '+%Y%m%d-080000')
logger -s -t findAllMatches "RUNTIME $SECONDS solving for ${startdt} to ${enddt}"

logger -s -t findAllMatches "RUNTIME $SECONDS start runDistrib"
$SRC/analysis/runDistrib.sh $MATCHSTART $MATCHEND


logger -s -t findAllMatches "RUNTIME $SECONDS start checkForFailures"
logf=$(ls -1tr $SRC/logs/matches-*.log | tail -1)
success=$(grep "Total run time:" $logf)

if [ "$success" == "" ]
then
    python -m utils.sendAnEmail markmcintyre99@googlemail.com "problem with matching" "Error"
    echo problems with solver
fi
logger -s -t findAllMatches "RUNTIME $SECONDS Solving Run Done"

logger -s -t findAllMatches "RUNTIME $SECONDS start rerunFailedLambdas"
python -m utils.rerunFailedLambdas

cd $here
logger -s -t findAllMatches "RUNTIME $SECONDS start reportOfLatestMatches"
python -m reports.reportOfLatestMatches $DATADIR/distrib $DATADIR $MATCHEND $rundate processed_trajectories.json

logger -s -t findAllMatches "RUNTIME $SECONDS start getMatchStats"
dailyrep=$(ls -1tr $DATADIR/dailyreports/20* | tail -1)
trajlist=$(cat $dailyrep | awk -F, '{print $2}')

matchlog=$( ls -1 ${SRC}/logs/matches-*.log | tail -1)
vals=$(python -m utils.getMatchStats $matchlog )
evts=$(echo $vals | awk '{print $2}')
trajs=$(echo $vals | awk '{print $6}')
matches=$(wc -l $dailyrep | awk '{print $1}')
rtim=$(echo $vals | awk '{print $7}')
echo $(basename $dailyrep) $evts $trajs $matches $rtim >>  $DATADIR/dailyreports/stats.txt

# copy stats to S3 so the daily report can run
if [ "$RUNTIME_ENV" == "PROD" ] ; then 
    aws s3 sync $DATADIR/dailyreports/ $UKMONSHAREDBUCKET/matches/RMSCorrelate/dailyreports/ --quiet
fi 

logger -s -t findAllMatches "RUNTIME $SECONDS start updateIndexPages"
$SRC/website/updateIndexPages.sh $dailyrep

logger -s -t findAllMatches "RUNTIME $SECONDS start purgeLogs"
find $SRC/logs -name "matches*" -mtime +7 -exec gzip {} \;
find $SRC/logs -name "matches*" -mtime +30 -exec rm -f {} \;

$SRC/utils/clearCaches.sh
logger -s -t findAllMatches "RUNTIME $SECONDS finished findAllMatches"