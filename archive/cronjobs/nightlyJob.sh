#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# script to update match data each night and then recalc any necessary orbits

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

logger -s -t nightlyJob "start nightlyJob" 

# dates to process for
rundate=$(date +%Y%m%d)
mth=$(date +%Y%m)
yr=$(date +%Y)
echo $rundate > $DATADIR/rundate.txt

# create the folder structure in case its missing
mkdir -p $DATADIR/{admin,browse,consolidated,costs,dailyreports,distrib,kmls}
mkdir -p $DATADIR/{lastlogs,latest,matched,orbits,reports,searchidx,single,trajdb,videos}
mkdir -p $DATADIR/browse/{annual,monthly,daily,showers}

####################################################################################
# START OF DATA PROCESSING. FIRST WE UPDATE THE SEARCH PAGE WITH SINGLE-STATION
# AND CAMERA DETAILS SO IT CAN BE SEARCHED WITHOUT WAITING FOR THE MATCHING ENGINE
####################################################################################

# update the JSON and html files containing camera and location details, used by the website
$SRC/website/updateCameraDets.sh

# consolidate the single-station data - we do this here so the search index can be updated earlier
# and we can search for single-station events without waiting for the main batch
$SRC/analysis/getRMSSingleData.sh
if [ "$(date +%m%d)" == "0101" ] ; then
    # catch any data uploaded on 01/01 that is for 31/12 the previous year
    $SRC/analysis/getRMSSingleData.sh $(date -d 'last year' +%Y)
fi

# now update the search index with single-station data
$SRC/analysis/createSearchable.sh $yr singles

####################################################################################
# NOW THE RUN THE MATCHING ENGINE VIA findAllmatches.sh
# Take care rerunning it as it will re-create the daily report
####################################################################################

# set up logging for the match process
matchlog=matchJob.log

# save the existing log, in case the process is being rerun on the same day
if [ "$(find $SRC/logs -name $matchlog -mmin +1380 -ls)" != "" ] ; then
    dt=$(stat $SRC/logs/$matchlog -c %y)
    suff=$(date --date ${dt:0:10} +%Y%m%d)
    mv -f $SRC/logs/$matchlog $SRC/logs/$matchlog-$suff
fi 

logger -s -t nightlyJob "start findAllMatches"
# Run the match process - run this only once as it scoops up all unprocessed data
${SRC}/analysis/findAllMatches.sh > ${SRC}/logs/${matchlog} 2>&1


####################################################################################
# FROM HERE DOWN WE'RE CONSOLIDATING DATA AND CREATING REPORTS
# and everything can be rerun safely provided the data are present
####################################################################################

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
aws s3 sync $SRC/share/ s3://ukmda-website/browse --exclude "*" --include "datadictionary.xlsx" --quiet

logger -s -t nightlyJog "finished nightlyJob"

# grab the logs for the website - run this last to capture the above Finished message
$SRC/analysis/getLogData.sh
