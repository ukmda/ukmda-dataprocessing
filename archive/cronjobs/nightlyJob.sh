#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# script to update match data each night and then recalc any necessary orbits

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

logger -s -t nightlyJob "RUNTIME $SECONDS start nightlyJob"

# dates to process for
rundate=$(date +%Y%m%d)
mth=$(date +%Y%m)
yr=$(date +%Y)
echo $rundate > $DATADIR/rundate.txt

# create the folder structure in case its missing
mkdir -p $DATADIR/{admin,browse,consolidated,costs,dailyreports,distrib,kmls}
mkdir -p $DATADIR/{lastlogs,latest,matched,orbits,reports,searchidx,single,trajdb,videos}
mkdir -p $DATADIR/browse/{annual,monthly,daily,showers}

# sync images, ftpdetect, platepars etc between this account and the old EE account
# this is needed because we want to keep the archive website on the old domain for now
# and it relies on some of these data
logger -s -t nightlyJob "RUNTIME $SECONDS synchronising data between accounts"
$SRC/utils/dataSync.sh 

mkdir -p $DATADIR/admin
logger -s -t nightlyJob "RUNTIME $SECONDS updating the camera location/dir/fov database"
python -c "from reports.CameraDetails import updateCamLocDirFovDB; updateCamLocDirFovDB();"
aws s3 cp $DATADIR/admin/cameraLocs.json $UKMONSHAREDBUCKET/admin/ --profile ukmonshared --quiet
aws s3 sync $UKMONSHAREDBUCKET/admin/ $DATADIR/admin --profile ukmonshared --quiet
aws s3 sync $UKMONSHAREDBUCKET/consolidated/ $DATADIR/consolidated/ --exclude "*" --include "camera-details.csv" --profile ukmonshared --quiet

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
    ${SRC}/website/createShwrExtracts.sh ${lastmth}28
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
python -c "from reports.createExchangeFiles import createAll; createAll();"
aws s3 sync $DATADIR/browse/daily/ $WEBSITEBUCKET/browse/daily/ --region eu-west-2 --quiet
aws s3 sync $DATADIR/browse/daily/ $OLDWEBSITEBUCKET/browse/daily/ --region eu-west-2 --quiet

logger -s -t nightlyJob "RUNTIME $SECONDS start createStationLoginTimes"
sudo grep publickey /var/log/secure | grep -v ec2-user | egrep "$(date "+%b %d")|$(date "+%b  %-d")" | awk '{printf("%s, %s\n", $3,$9)}' > $DATADIR/reports/stationlogins.txt
aws s3 cp $DATADIR/reports/stationlogins.txt $WEBSITEBUCKET/reports/stationlogins.txt --region eu-west-2 --quiet
aws s3 cp $DATADIR/reports/stationlogins.txt $OLDWEBSITEBUCKET/reports/stationlogins.txt --region eu-west-2 --quiet

cd $DATADIR
# do this manually when on PC required as it requires too much memory for the batch server; closes #61
#python $PYLIB/maintenance/plotStationsOnMap.py False
aws s3 cp $DATADIR/stations.png $WEBSITEBUCKET/ --region eu-west-2 --quiet
aws s3 cp $DATADIR/stations.png $OLDWEBSITEBUCKET/ --region eu-west-2 --quiet

rm -f $SRC/data/.nightly_running

logger -s -t nightlyJob "RUNTIME $SECONDS start getBadStations"
$SRC/analysis/getBadStations.sh

logger -s -t nightlyJob "RUNTIME $SECONDS start costReport"
$SRC/website/costReport.sh

# set time of next run
python $PYLIB/maintenance/getNextBatchStart.py 150

# create station reports. This takes hours hence done after everything else
#if [ "$(date +%a)" == "Sun" ] ; then 
    logger -s -t nightlyJob "RUNTIME $SECONDS start stationReports"
    $SRC/analysis/stationReports.sh
#fi

logger -s -t nightlyJob "RUNTIME $SECONDS synchronising raw data only back again"
$SRC/utils/dataSyncBack.sh 

logger -s -t nightlyJob "RUNTIME $SECONDS start clearSpace"
$SRC/utils/clearSpace.sh 

logger -s -t nightlyJob "RUNTIME $SECONDS finished nightlyJob"

# grab the logs for the website - run this last to capture the above Finished message
$SRC/analysis/getLogData.sh



