#!/bin/bash
#
# script to update match data each night and then recalc any necessary orbits

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1
export SRC
source ~/venvs/$WMPL_ENV/bin/activate
export PYTHONPATH=$PYLIB:$wmpl_loc

logger -s -t nightlyJob "starting"

# dates to process for
mth=`date '+%Y%m'`
yr=`date '+%Y'`

# force-consolidate any outstanding new data 
logger -s -t nightlyJob "forcing consolidation of anything pending"
source $WEBSITEKEY
export AWS_DEFAULT_REGION=eu-west-2
aws lambda invoke --function-name ConsolidateCSVs --log-type Tail $SRC/logs/ConsolidateCSVs.log

# get a list of all jpgs from single station events for later use
logger -s -t nightlyJob "getting list of single jpg files"
aws s3 ls $WEBSITEBUCKET/img/single/$yr/ --recursive | awk '{print $4}' > $DATADIR/singleJpgs.csv

logger -s -t nightlyJob "getting latest consolidated information"
source $UKMONSHAREDKEY
aws s3 sync s3://ukmon-shared/consolidated/ ${DATADIR}/consolidated --exclude 'consolidated/temp/*' --quiet

logger -s -t updateSearchIndex "getting latest livefeed CSV files"
qmth=$(date +%m)
cq=$(((qmth - 1 ) / 3 + 1))
lq=$(((qmth - 1 ) / 3 ))
aws s3 cp s3://ukmon-live/idx${yr}0${cq}.csv ${DATADIR}/ukmonlive/
aws s3 cp s3://ukmon-live/idx${yr}0${lq}.csv ${DATADIR}/ukmonlive/

# run this only once as it scoops up all unprocessed data
logger -s -t nightlyJob "looking for matching events and solving their trajectories"
matchlog=matches-$(date +%Y%m%d-%H%M%S).log
${SRC}/analysis/findAllMatches.sh > ${SRC}/logs/matches/${matchlog} 2>&1

# send daily report - only want to do this if in batch mode
if [ "`tty`" != "not a tty" ]; then 
    logger -s -t nightlyJob 'got a tty, not triggering report'
else 
    logger -s -t nightlyJob 'no tty, triggering report' 
    source $WEBSITEKEY
    export AWS_DEFAULT_REGION=eu-west-1
    aws lambda invoke --function-name dailyReport --log-type Tail $SRC/logs/dailyReport.log
fi

logger -s -t nightlyJob "update shower associations"
daysback=$MATCHSTART
${SRC}/analysis/updateRMSShowerAssocs.sh $daysback

logger -s -t nightlyJob "consolidate the resulting data "
$SRC/analysis/consolidateOutput.sh ${yr}

logger -s -t nightlyJob "create monthly and shower extracts for the website"
${SRC}/website/createMthlyExtracts.sh ${mth}
${SRC}/website/createShwrExtracts.sh ${mth}
${SRC}/website/createFireballPage.sh

logger -s -t nightlyJob "update search index"
${SRC}/analysis/updateSearchIndex.sh

logger -s -t nightlyJob "update the R version of the camera info file"
python << EOD
import fileformats.CameraDetails as cc
s = cc.SiteInfo()
s.saveAsR('${RCODEDIR}/CONFIG/StationList.r')
EOD

logger -s -t nightlyJob "update the annual report for this year"
$SRC/analysis/showerReport.sh ALL $yr force

logger -s -t nightlyJob "update other relevant showers"
${SRC}/analysis/reportYear.sh ${yr}

logger -s -t nightlyJob "create the cover page for the website"
${SRC}/website/createSummaryTable.sh

logger -s -t nightlyJob "create station status report"
${SRC}/website/cameraStatusReport.sh

logger -s -t nightlyJob "create event log for other networks"
python $SRC/ukmon_pylib/reports/createExchangeFiles.py

logger -s -t nightlyJob "Create density and velocity plots by solar longitude"
# too slow for now commented out
# $SRC/analysis/createDensityPlots.sh

logger -s -t nightlyJob "clean up old logs"
find $SRC/logs -name "nightly*.gz" -mtime +90 -exec rm -f {} \;
find $SRC/logs -name "nightly*.log" -mtime +7 -exec gzip {} \;

logger -s -t nightlyJob "Finished"
rm -f $SRC/data/.nightly_running

# create performance metrics
cd $SRC/logs
matchlog=$( ls -1 ${SRC}/logs/matches/matches-*.log | tail -1)
python $SRC/ukmon_pylib/metrics/timingMetrics.py $matchlog 'M' >> $SRC/logs/perfMatching.csv

nightlog=$( ls -1 ${SRC}/logs/nightlyJob-*.log | tail -1)
python $SRC/ukmon_pylib/metrics/timingMetrics.py $nightlog 'N' >> $SRC/logs/perfNightly.csv
