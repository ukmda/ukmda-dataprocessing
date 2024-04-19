#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# script to update match data each night and then recalc any necessary orbits

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

NJLOGSTREAM=$(date +%Y%m%d-%H%M%S)
export NJLOGSTREAM
aws logs create-log-stream --log-group-name $NJLOGGRP --log-stream-name $NJLOGSTREAM --profile ukmonshared

# log2cw is a function defined in config.ini and logs to cloudwatch, syslog and console
log2cw $NJLOGGRP $NJLOGSTREAM "start nightlyJob" nightlyJob

# dates to process for
rundate=$(date +%Y%m%d)
mth=$(date +%Y%m)
yr=$(date +%Y)
echo $rundate > $DATADIR/rundate.txt

# create the folder structure in case its missing
mkdir -p $DATADIR/{admin,browse,consolidated,costs,dailyreports,distrib,kmls}
mkdir -p $DATADIR/{lastlogs,latest,matched,orbits,reports,searchidx,single,trajdb,videos}
mkdir -p $DATADIR/browse/{annual,monthly,daily,showers}

log2cw $NJLOGGRP $NJLOGSTREAM "updating the camera location/dir/fov database" nightlyJob
python -c "from reports.CameraDetails import updateCamLocDirFovDB; updateCamLocDirFovDB();"
aws s3 cp $DATADIR/admin/cameraLocs.json $UKMONSHAREDBUCKET/admin/ --profile ukmonshared --quiet
aws s3 sync $UKMONSHAREDBUCKET/admin/ $DATADIR/admin --profile ukmonshared --quiet

# create the CSV file of camera info, and the html versions for search functions on the website
log2cw $NJLOGGRP $NJLOGSTREAM "updating the camera details files for searching" nightlyJob
python -c "from reports.CameraDetails import createCDCsv; createCDCsv('consolidated');"
aws s3 cp $DATADIR/consolidated/camera-details.csv $UKMONSHAREDBUCKET/consolidated/ --profile ukmonshared --quiet
aws s3 cp $DATADIR/statopts.html $WEBSITEBUCKET/search/ --profile ukmonshared --quiet
aws s3 cp $DATADIR/activestatopts.html $WEBSITEBUCKET/search/ --profile ukmonshared --quiet
aws s3 cp $DATADIR/activestatlocs.html $WEBSITEBUCKET/search/ --profile ukmonshared --quiet

# run this only once as it scoops up all unprocessed data
log2cw $NJLOGGRP $NJLOGSTREAM "start findAllMatches" nightlyJob
matchlog=matchJob.log
if [ -f $SRC/logs/$matchlog ] ; then
    suff=$(stat matchJob.log -c %X)
    mv $SRC/logs/$matchlog $SRC/logs/$matchlog-$suff
fi 
${SRC}/analysis/findAllMatches.sh > ${SRC}/logs/${matchlog} 2>&1

log2cw $NJLOGGRP $NJLOGSTREAM "start consolidateOutput" nightlyJob 
$SRC/analysis/consolidateOutput.sh ${yr}

log2cw $NJLOGGRP $NJLOGSTREAM "start createSearchable pass 2" nightlyJob 
$SRC/analysis/createSearchable.sh $yr matches

# add daily report to the website
log2cw $NJLOGGRP $NJLOGSTREAM "start publishDailyReport" nightlyJob 
$SRC/website/publishDailyReport.sh 

log2cw $NJLOGGRP $NJLOGSTREAM "start createMthlyExtracts" nightlyJob 
${SRC}/website/createMthlyExtracts.sh ${mth}

log2cw $NJLOGGRP $NJLOGSTREAM "start createShwrExtracts" nightlyJob 
${SRC}/website/createShwrExtracts.sh ${rundate}

log2cw $NJLOGGRP $NJLOGSTREAM "start createFireballPage" nightlyJob 
#requires search index to have been updated first 
${SRC}/website/createFireballPage.sh ${yr} -3.99

log2cw $NJLOGGRP $NJLOGSTREAM "start showerReport ALL $mth" nightlyJob 
$SRC/analysis/showerReport.sh ALL ${mth} force

log2cw $NJLOGGRP $NJLOGSTREAM "start showerReport ALL $yr" nightlyJob 
$SRC/analysis/showerReport.sh ALL ${yr} force

# if we ran on the 1st of the month we need to catch any late-arrivals for last month
if [ $(date +%d) -eq 1 ] ; then
    lastmth=$(date -d '-1 month' +%Y%m)
    log2cw $NJLOGGRP $NJLOGSTREAM "start showerMthlyExtracts ALL $lastmth" nightlyJob
    ${SRC}/website/createMthlyExtracts.sh ${lastmth}
    log2cw $NJLOGGRP $NJLOGSTREAM "start createShwrExtracts ALL $lastmth" nightlyJob
    ${SRC}/website/createShwrExtracts.sh ${lastmth}28
    log2cw $NJLOGGRP $NJLOGSTREAM "start showerReport ALL $lastmth" nightlyJob
    $SRC/analysis/showerReport.sh ALL ${lastmth} force
fi 

log2cw $NJLOGGRP $NJLOGSTREAM "start reportActiveShowers" nightlyJob
${SRC}/analysis/reportActiveShowers.sh ${yr}

log2cw $NJLOGGRP $NJLOGSTREAM "start createSummaryTable" nightlyJob
${SRC}/website/createSummaryTable.sh

log2cw $NJLOGGRP $NJLOGSTREAM "start cameraStatusReport" nightlyJob
${SRC}/website/cameraStatusReport.sh $rundate

log2cw $NJLOGGRP $NJLOGSTREAM "start createExchangeFiles" nightlyJob
python -c "from reports.createExchangeFiles import createAll;createAll();"
aws s3 sync $DATADIR/browse/daily/ $WEBSITEBUCKET/browse/daily/ --region eu-west-2 --quiet

cd $DATADIR
# do this manually when on PC required as it requires too much memory for the batch server; closes #61
# python $PYLIB/maintenance/plotStationsOnMap.py False
aws s3 cp $DATADIR/stations.png $WEBSITEBUCKET/ --region eu-west-2 --quiet

rm -f $SRC/data/.nightly_running

log2cw $NJLOGGRP $NJLOGSTREAM "start getBadStations" nightlyJob
$SRC/analysis/getBadStations.sh

log2cw $NJLOGGRP $NJLOGSTREAM "start costReport" nightlyJob
$SRC/website/costReport.sh

# set time of next run
python $PYLIB/maintenance/getNextBatchStart.py 150

# create station reports. This takes hours hence done after everything else
log2cw $NJLOGGRP $NJLOGSTREAM "start stationReports" nightlyJob
$SRC/analysis/stationReports.sh

log2cw $NJLOGGRP $NJLOGSTREAM "start clearSpace" nightlyJob
$SRC/utils/clearSpace.sh 

log2cw $NJLOGGRP $NJLOGSTREAM "update MariaDB tables" nightlyJob
$SRC/utils/loadMatchCsvMDB.sh
$SRC/utils/loadSingleCsvMDB.sh

log2cw $NJLOGGRP $NJLOGSTREAM "finished nightlyJob" nightlyJob

# grab the logs for the website - run this last to capture the above Finished message
$SRC/analysis/getLogData.sh



