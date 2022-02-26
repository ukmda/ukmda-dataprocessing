#!/bin/bash
#
# script to update match data each night and then recalc any necessary orbits

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1
source $HOME/venvs/$WMPL_ENV/bin/activate

logger -s -t nightlyJob "starting"

# dates to process for
rundate=$(date +%Y%m%d)
mth=$(date +%Y%m)
yr=$(date +%Y)
echo $rundate > $DATADIR/rundate.txt

source $WEBSITEKEY
export AWS_DEFAULT_REGION=eu-west-2

# run this only once as it scoops up all unprocessed data
logger -s -t nightlyJob "looking for matching events and solving their trajectories"
matchlog=matches-$(date +%Y%m%d-%H%M%S).log
${SRC}/analysis/findAllMatches.sh > ${SRC}/logs/${matchlog} 2>&1

logger -s -t nightlyJob "waiting for lambdas to finish"
# need to wait here till the lambdas creating orbit pages are finished
sleep 600
# catchall to reprocess any failed orbit page updates
python -m utils.rerunFailedGetExtraFiles

# send daily report - only want to do this if in batch mode
if [ "`tty`" != "not a tty" ]; then 
    logger -s -t nightlyJob 'got a tty, not triggering report'
else 
    logger -s -t nightlyJob 'no tty, triggering report' 
    source $WEBSITEKEY
    export AWS_DEFAULT_REGION=eu-west-1
    aws lambda invoke --function-name dailyReport --log-type Tail $SRC/logs/dailyReport.log
fi

logger -s -t nightlyJob "consolidate the resulting data"
$SRC/analysis/consolidateOutput.sh ${yr}

logger -s -t nightlyJob "create monthly and shower extracts for the website"
${SRC}/website/createMthlyExtracts.sh ${mth}
${SRC}/website/createShwrExtracts.sh ${mth}

logger -s -t nightlyJob "update search index files and station list for search index"
$SRC/analysis/createSearchable.sh
$SRC/website/createStationList.sh

logger -s -t nightlyJob "update annual bright event/fireball page"
#requires search index to have been updated first 
${SRC}/website/createFireballPage.sh ${yr} -3.7

logger -s -t nightlyJob "update the R version of the camera info file"
python << EOD
import fileformats.CameraDetails as cc
s = cc.SiteInfo()
s.saveAsR('${RCODEDIR}/CONFIG/StationList.r')
EOD

logger -s -t nightlyJob "update the monthly and annual reports"
$SRC/analysis/showerReport.sh ALL ${mth} force
$SRC/analysis/showerReport.sh ALL ${yr} force

logger -s -t nightlyJob "Create density and velocity plots by solar longitude"
# do this before individual shower reports so that the graphs can be copied
$SRC/analysis/createDensityPlots.sh ${mth}
$SRC/analysis/createDensityPlots.sh ${yr}

logger -s -t nightlyJob "update other relevant showers"
${SRC}/analysis/reportYear.sh ${yr}

logger -s -t nightlyJob "create the cover page for the website"
${SRC}/website/createSummaryTable.sh

logger -s -t nightlyJob "create station status report"
${SRC}/website/cameraStatusReport.sh

logger -s -t nightlyJob "create event log for other networks"
python -m reports.createExchangeFiles

logger -s -t nightlyJob "create list of connected stations and map of stations"
sudo grep publickey /var/log/secure | grep -v ec2-user | egrep "$(date "+%b %d")|$(date "+%b  %-d")" | awk '{printf("%s, %s\n", $3,$9)}' > $DATADIR/reports/stationlogins.txt

cd $DATADIR
# do this manually when on PC required; closes #61
#python $PYLIB/utils/plotStationsOnMap.py $CAMINFO

source $WEBSITEKEY
aws s3 cp $DATADIR/reports/stationlogins.txt $WEBSITEBUCKET/reports/stationlogins.txt --quiet
aws s3 cp $DATADIR/stations.png $WEBSITEBUCKET/ --quiet

logger -s -t nightlyJob "create station reports"
$SRC/analysis/stationReports.sh

source $WEBSITEKEY
python -m metrics.camMetrics $rundate
cat $DATADIR/reports/camuploadtimes.csv  | sort -n -t ',' -k2 > /tmp/tmp444.txt
mv -f /tmp/tmp444.txt $DATADIR/reports/camuploadtimes.csv

logger -s -t nightlyJob "clean up old logs"
find $SRC/logs -name "nightly*.gz" -mtime +90 -exec rm -f {} \;
find $SRC/logs -name "nightly*.log" -mtime +7 -exec gzip {} \;

rm -f $SRC/data/.nightly_running

# create performance metrics
cd $SRC/logs
matchlog=$( ls -1 ${SRC}/logs/matches-*.log | tail -1)
python -m metrics.timingMetrics $matchlog 'M' >> $SRC/logs/perfMatching.csv

nightlog=$( ls -1 ${SRC}/logs/nightlyJob-*.log | tail -1)
python -m metrics.timingMetrics $nightlog 'N' >> $SRC/logs/perfNightly.csv

# check for bad stations
$SRC/analysis/getBadStations.sh
logger -s -t nightlyJob "Finished"

