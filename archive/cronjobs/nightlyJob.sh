#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# script to update match data each night and then recalc any necessary orbits

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

logger -s -t $(basename $0 .sh) "starting"

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
# This section is safe to rerun at any time. 
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

# Run the match process - run this only once as it scoops up all unprocessed data
${SRC}/analysis/findAllMatches.sh > ${SRC}/logs/${matchlog} 2>&1


####################################################################################
# FROM HERE DOWN WE'RE CONSOLIDATING DATA AND CREATING REPORTS
# and everything can be rerun safely provided the data are present
####################################################################################

$SRC/analysis/rerunAllReports.sh ${yr} ${rundate}

logger -s -t $(basename $0 .sh) "finished"

rm -f $SRC/data/.nightly_running

# grab the logs for the website - run this last to capture the above Finished message
$SRC/analysis/getLogData.sh
