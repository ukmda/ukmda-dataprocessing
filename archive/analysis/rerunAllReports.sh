#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# script to update match data each night and then recalc any necessary orbits

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

logger -s -t $(basename $0 .sh) "starting"

# dates to process for
if [ "$1" == "" ] ; then
    rundate=$(date +%Y%m%d)
    mth=$(date +%Y%m)
    yr=$(date +%Y)
else
    rundate=$1
    mth=${rundate:0:6}
    yr=${rundate:0:4}
fi

logger -s -t $(basename $0 .sh) "running all reporting for for rundate ${rundate} month ${mth} year ${yr}"

# update the website daily, monthly and annual index pages where needed
$SRC/website/updateIndexPages.sh

# consolidate the output of the match process for further analysis
$SRC/analysis/consolidateOutput.sh ${yr}
if [ "$(date +%m%d)" == "0101" ] ; then
    # catch any data uploaded on 01/01 that is for 31/12 the previous year
    $SRC/analysis/consolidateOutput.sh $(date -d 'last year' +%Y)
fi 

# update the search indexes used on the website
$SRC/analysis/createSearchable.sh $yr matches

# add daily report to the website
$SRC/website/publishDailyReport.sh 

# create monthly and per-shower CSV extracts of the data
${SRC}/website/createMthlyExtracts.sh ${mth}
${SRC}/website/createShwrExtracts.sh ${rundate}

# create the fireballs page
#requires search index to have been updated first 
${SRC}/website/createFireballPage.sh ${yr} -3.99

# create a report of activity for the current month and whole year 
$SRC/analysis/showerReport.sh ALL ${mth} force
$SRC/analysis/showerReport.sh ALL ${yr} force

# if we ran on the 1st of the month we need to catch any late-arrivals for last month
if [ $(date +%d) -eq 1 ] ; then
    lastmth=$(date -d '-1 month' +%Y%m)
    ${SRC}/website/createMthlyExtracts.sh ${lastmth}
    ${SRC}/website/createShwrExtracts.sh ${lastmth}28
    $SRC/analysis/showerReport.sh ALL ${lastmth} force
fi 

# create a per-shower report for any currently active showers
${SRC}/analysis/reportActiveShowers.sh ${yr}

# create the website front page
${SRC}/website/createSummaryTable.sh

# create the camera status reports
${SRC}/website/cameraStatusReport.sh $rundate

# create the files for exchange with other networks - i think this is unused
python -c "from reports.createExchangeFiles import createAll;createAll();"
aws s3 sync $DATADIR/browse/daily/ $WEBSITEBUCKET/browse/daily/ --quiet

cd $DATADIR
# do this manually when on PC required as it requires too much memory for the batch server; closes #61
# python $PYLIB/maintenance/plotStationsOnMap.py False
aws s3 cp $DATADIR/stations.png $WEBSITEBUCKET/  --quiet

rm -f $SRC/data/.nightly_running

# various reports for management - bad stations, costs, next batch start time.
$SRC/analysis/getBadStations.sh
$SRC/website/costReport.sh
python $PYLIB/maintenance/getNextBatchStart.py 150

# create station reports. This takes a while hence done after everything else
$SRC/analysis/stationReports.sh

# clear down space where possible
$SRC/utils/clearSpace.sh 

# load the MariaDB with the latest data. The mariadb database isn't used much
$SRC/utils/loadMatchCsvMDB.sh
$SRC/utils/loadSingleCsvMDB.sh

# rerun the job to plot solar longitude graphs and update the database of used/unused detections
# has to be run quite late as not all trajectories have synced to the website earlier
$SRC/analysis/updatePlotsAndDetStatus.sh

# push the API data dictionary to the website for end-user use
aws s3 sync $DATADIR/share/ s3://ukmda-website/browse --exclude "*" --include "datadictionary.xlsx" --quiet

logger -s -t $(basename $0 .sh) "finished"
