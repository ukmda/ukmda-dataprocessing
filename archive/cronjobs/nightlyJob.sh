#!/bin/bash
#
# script to update match data each night and then recalc any necessary orbits

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
source $HOME/venvs/$WMPL_ENV/bin/activate

logger -s -t nightlyJob "RUNTIME $SECONDS start nightlyJob"

# dates to process for
rundate=$(date +%Y%m%d)
mth=$(date +%Y%m)
yr=$(date +%Y)
echo $rundate > $DATADIR/rundate.txt

python -c "from fileformats.CameraDetails import updateCamLocDirFovDB; updateCamLocDirFovDB();"
aws s3 cp $DATADIR/admin/cameraLocs.json $UKMONSHAREDBUCKET/admin/ --region eu-west-2

# run this only once as it scoops up all unprocessed data
logger -s -t nightlyJob "RUNTIME $SECONDS start findAllMatches"
matchlog=matches-$(date +%Y%m%d-%H%M%S).log
${SRC}/analysis/findAllMatches.sh > ${SRC}/logs/${matchlog} 2>&1

logger -s -t nightlyJob "RUNTIME $SECONDS start consolidateOutput"
$SRC/analysis/consolidateOutput.sh ${yr}

logger -s -t nightlyJob "RUNTIME $SECONDS start createSearchable pass 2"
$SRC/analysis/createSearchable.sh $yr matches

logger -s -t nightlyJob "RUNTIME $SECONDS start createStationList"
$SRC/website/createStationList.sh

# send daily report - only want to do this if in batch mode
if [ "`tty`" != "not a tty" ]; then 
    echo 'got a tty, not triggering report'
else 
    aws lambda invoke --function-name 822069317839:function:dailyReport --region eu-west-1 --log-type None $SRC/logs/dailyReport.log
fi
# add daily report to the website
logger -s -t nightlyJob "RUNTIME $SECONDS start publishDailyReport"
$SRC/website/publishDailyReport.sh 

logger -s -t nightlyJob "RUNTIME $SECONDS start createMthlyExtracts"
${SRC}/website/createMthlyExtracts.sh ${mth}

logger -s -t nightlyJob "RUNTIME $SECONDS start createShwrExtracts"
${SRC}/website/createShwrExtracts.sh ${rundate}

logger -s -t nightlyJob "RUNTIME $SECONDS start createFireballPage"
#requires search index to have been updated first 
${SRC}/website/createFireballPage.sh ${yr} -3.99

logger -s -t nightlyJob "RUNTIME $SECONDS start showerReport ALL $mth"
$SRC/analysis/showerReport.sh ALL ${mth} force

logger -s -t nightlyJob "RUNTIME $SECONDS start showerReport ALL $yr"
$SRC/analysis/showerReport.sh ALL ${yr} force

# if we ran on the 1st of the month we need to catch any late-arrivals for last month
if [ $(date +%d) -eq 1 ] ; then
    lastmth=$(date -d '-1 month' +%Y%m)
    logger -s -t nightlyJob "RUNTIME $SECONDS start showerMthlyExtracts ALL $lastmth"
    ${SRC}/website/createMthlyExtracts.sh ${lastmth}
    logger -s -t nightlyJob "RUNTIME $SECONDS start showerShwrExtracts ALL $lastmth"
    ${SRC}/website/createShwrExtracts.sh ${lastmth}
    logger -s -t nightlyJob "RUNTIME $SECONDS start showerReport ALL $lastmth"
    $SRC/analysis/showerReport.sh ALL ${lastmth} force
fi 

logger -s -t nightlyJob "RUNTIME $SECONDS start reportActiveShowers"
${SRC}/analysis/reportActiveShowers.sh ${yr}

logger -s -t nightlyJob "RUNTIME $SECONDS start createSummaryTable"
${SRC}/website/createSummaryTable.sh

logger -s -t nightlyJob "RUNTIME $SECONDS start camMetrics"
python -m metrics.camMetrics $rundate

logger -s -t nightlyJob "RUNTIME $SECONDS start cameraStatusReport"
${SRC}/website/cameraStatusReport.sh

logger -s -t nightlyJob "RUNTIME $SECONDS start createExchangeFiles"
python -m reports.createExchangeFiles
aws s3 sync $DATADIR/browse/daily/ $WEBSITEBUCKET/browse/daily/ --region eu-west-2 --quiet

logger -s -t nightlyJob "RUNTIME $SECONDS start createStationLoginTimes"
sudo grep publickey /var/log/secure | grep -v ec2-user | egrep "$(date "+%b %d")|$(date "+%b  %-d")" | awk '{printf("%s, %s\n", $3,$9)}' > $DATADIR/reports/stationlogins.txt
aws s3 cp $DATADIR/reports/stationlogins.txt $WEBSITEBUCKET/reports/stationlogins.txt --region eu-west-2 --quiet

cd $DATADIR
# do this manually when on PC required; closes #61
#python $PYLIB/utils/plotStationsOnMap.py $DATADIR/consolidated/camera-details.csv
aws s3 cp $DATADIR/stations.png $WEBSITEBUCKET/ --region eu-west-2 --quiet

rm -f $SRC/data/.nightly_running

logger -s -t nightlyJob "RUNTIME $SECONDS start getBadStations"
$SRC/analysis/getBadStations.sh

logger -s -t nightlyJob "RUNTIME $SECONDS start costReport"
$SRC/website/costReport.sh

# set time of next run
python $PYLIB/utils/getNextBatchStart.py 150

# create station reports. This takes hours hence done after everything else
#if [ "$(date +%a)" == "Sun" ] ; then 
    logger -s -t nightlyJob "RUNTIME $SECONDS start stationReports"
    $SRC/analysis/stationReports.sh
#fi

logger -s -t nightlyJob "RUNTIME $SECONDS start clearSpace"
$SRC/utils/clearSpace.sh 

logger -s -t nightlyJob "RUNTIME $SECONDS finished nightlyJob"

# grab the logs for the website - run this last to capture the above Finished message
$SRC/analysis/getLogData.sh



