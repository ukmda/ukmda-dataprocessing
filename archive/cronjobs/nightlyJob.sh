#!/bin/bash
#
# script to update match data each night and then recalc any necessary orbits

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
source $HOME/venvs/$WMPL_ENV/bin/activate
$SRC/utils/clearCaches.sh

logger -s -t nightlyJob "starting"
logger -s -t nightlyJob "RUNTIME $SECONDS nightlyJob"

# dates to process for
rundate=$(date +%Y%m%d)
mth=$(date +%Y%m)
yr=$(date +%Y)
echo $rundate > $DATADIR/rundate.txt

logger -s -t nightlyJob "update search index files with singleton data"
logger -s -t nightlyJob "RUNTIME $SECONDS createSearchable"
$SRC/analysis/createSearchable.sh

python -c "from fileformats.CameraDetails import updateCamLocDirFovDB; updateCamLocDirFovDB();"
aws s3 cp $DATADIR/admin/cameraLocs.json s3://ukmon-shared/admin/ --region eu-west-2

# run this only once as it scoops up all unprocessed data
logger -s -t nightlyJob "looking for matching events and solving their trajectories"
logger -s -t nightlyJob "RUNTIME $SECONDS findAllMatches"
matchlog=matches-$(date +%Y%m%d-%H%M%S).log
${SRC}/analysis/findAllMatches.sh > ${SRC}/logs/${matchlog} 2>&1

$SRC/utils/clearCaches.sh

logger -s -t nightlyJob "consolidate the resulting data"
logger -s -t nightlyJob "RUNTIME $SECONDS consolidateOutput"
$SRC/analysis/consolidateOutput.sh ${yr}

logger -s -t nightlyJob "reupdate search index files to collect matches"
logger -s -t nightlyJob "RUNTIME $SECONDS createSearchable"
$SRC/analysis/createSearchable.sh

logger -s -t nightlyJob "update station list"
logger -s -t nightlyJob "RUNTIME $SECONDS createStationList"
$SRC/website/createStationList.sh

# send daily report - only want to do this if in batch mode
if [ "`tty`" != "not a tty" ]; then 
    logger -s -t nightlyJob 'got a tty, not triggering report'
else 
    logger -s -t nightlyJob 'no tty, triggering report' 
    aws lambda invoke --function-name 822069317839:function:dailyReport --region eu-west-1 --log-type None $SRC/logs/dailyReport.log
fi
# add daily report to the website
logger -s -t nightlyJob "RUNTIME $SECONDS publishDailyReport"
$SRC/website/publishDailyReport.sh 

logger -s -t nightlyJob "create monthly extracts for the website"
logger -s -t nightlyJob "RUNTIME $SECONDS createMthlyExtracts"
${SRC}/website/createMthlyExtracts.sh ${mth}

logger -s -t nightlyJob "create shower extracts for the website"
logger -s -t nightlyJob "RUNTIME $SECONDS createShwrExtracts"
${SRC}/website/createShwrExtracts.sh ${mth}

logger -s -t nightlyJob "update annual bright event/fireball page"
logger -s -t nightlyJob "RUNTIME $SECONDS createFireballPage"
#requires search index to have been updated first 
${SRC}/website/createFireballPage.sh ${yr} -3.99

logger -s -t nightlyJob "update the monthly reports"
logger -s -t nightlyJob "RUNTIME $SECONDS showerReport ALL $mth"
$SRC/analysis/showerReport.sh ALL ${mth} force

logger -s -t nightlyJob "update the annual reports"
logger -s -t nightlyJob "RUNTIME $SECONDS showerReport ALL $yr"
$SRC/analysis/showerReport.sh ALL ${yr} force

# if we ran on the 1st of the month we need to catch any late-arrivals for last month
if [ $(date +%d) -eq 1 ] ; then
    logger -s -t nightlyJob "update last months data too"
    logger -s -t nightlyJob "RUNTIME $SECONDS last month"
    lastmth=$(date -d '-1 month' +%Y%m)
    ${SRC}/website/createMthlyExtracts.sh ${lastmth}
    ${SRC}/website/createShwrExtracts.sh ${lastmth}
    $SRC/analysis/showerReport.sh ALL ${lastmth} force
fi 

logger -s -t nightlyJob "update other relevant showers"
logger -s -t nightlyJob "RUNTIME $SECONDS reportActiveShowers"
${SRC}/analysis/reportActiveShowers.sh ${yr}

logger -s -t nightlyJob "create the cover page for the website"
logger -s -t nightlyJob "RUNTIME $SECONDS createSummaryTable"
${SRC}/website/createSummaryTable.sh

logger -s -t nightlyJob "create station status report"
logger -s -t nightlyJob "RUNTIME $SECONDS cameraStatusReport"
${SRC}/website/cameraStatusReport.sh

logger -s -t nightlyJob "create event log for other networks"
logger -s -t nightlyJob "RUNTIME $SECONDS createExchangeFiles"
python -m reports.createExchangeFiles
aws s3 sync $DATADIR/browse/daily/ $WEBSITEBUCKET/browse/daily/ --region eu-west-2 --quiet

logger -s -t nightlyJob "create list of connected stations and map of stations"
logger -s -t nightlyJob "RUNTIME $SECONDS ccameralist"
sudo grep publickey /var/log/secure | grep -v ec2-user | egrep "$(date "+%b %d")|$(date "+%b  %-d")" | awk '{printf("%s, %s\n", $3,$9)}' > $DATADIR/reports/stationlogins.txt

cd $DATADIR
# do this manually when on PC required; closes #61
#python $PYLIB/utils/plotStationsOnMap.py $CAMINFO

aws s3 cp $DATADIR/reports/stationlogins.txt $WEBSITEBUCKET/reports/stationlogins.txt --region eu-west-2 --quiet
aws s3 cp $DATADIR/stations.png $WEBSITEBUCKET/ --region eu-west-2 --quiet

logger -s -t nightlyJob "Create camera metrics"
logger -s -t nightlyJob "RUNTIME $SECONDS camMetrics"
python -m metrics.camMetrics $rundate
cat $DATADIR/reports/camuploadtimes.csv  | sort -n -t ',' -k2 > /tmp/tmp444.txt
mv -f /tmp/tmp444.txt $DATADIR/reports/camuploadtimes.csv

rm -f $SRC/data/.nightly_running

logger -s -t nightlyJob "check for bad stations"
logger -s -t nightlyJob "RUNTIME $SECONDS getBadStations"
$SRC/analysis/getBadStations.sh


logger -s -t nightlyJob "update the costs page"
logger -s -t nightlyJob "RUNTIME $SECONDS costReport"
$SRC/website/costReport.sh

# set time of next run
python $PYLIB/utils/getNextBatchStart.py 150

# create station reports. This takes hours hence done after everything else
if [ "$(date +%a)" == "Sun" ] ; then 
    logger -s -t nightlyJob "create station reports"
    logger -s -t nightlyJob "RUNTIME $SECONDS stationReports"
    $SRC/analysis/stationReports.sh
fi

logger -s -t nightlyJob "clear down old logfiles etc"
logger -s -t nightlyJob "RUNTIME $SECONDS clearSpace"
$SRC/utils/clearSpace.sh 

logger -s -t nightlyJob "Finished"
logger -s -t nightlyJob "RUNTIME $SECONDS finished"

# grab the logs for the website - run this last to capture the above Finished message
$SRC/analysis/getLogData.sh



