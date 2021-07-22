#!/bin/bash
#
# script to update match data each night and then recalc any necessary orbits

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1
source ~/venvs/$WMPL_ENV/bin/activate

# so i can import the config file into python functions
export CONFIG

# to run various python processes
export PYTHONPATH=$PYLIB:$wmpl_loc

thismth=`date '+%Y%m'`
thisyr=`date '+%Y'`

source $WEBSITEKEY
export AWS_DEFAULT_REGION=eu-west-2
aws lambda invoke --function-name ConsolidateCSVs --log-type Tail $SRC/logs/ConsolidateCSVs.log

# run this only once as it scoops up all unprocessed data
logger -s -t nightlyJob "looking for matching events and solving their trajectories"
matchlog=matches-$(date +%Y%m%d-%H%M%S).log
${SRC}/analysis/findAllMatches.sh ${thismth} > ${SRC}/logs/matches/${matchlog} 2>&1

# send daily report - only want to do this if in batch mode
if [ "`tty`" != "not a tty" ]; then 
    logger -s -t nightlyJob 'got a tty, not triggering report'
else 
    logger -s -t nightlyJob 'no tty, triggering report' 
    source $WEBSITEKEY
    export AWS_DEFAULT_REGION=eu-west-1
    aws lambda invoke --function-name dailyReport --log-type Tail $SRC/logs/dailyReport.log
fi

logger -s -t nightlyJob "update shower associations, then create monthly and shower extracts for the website"

${SRC}/analysis/updateRMSShowerAssocs.sh ${thismth}
${SRC}/website/createMthlyExtracts.sh ${thismth}
${SRC}/website/createShwrExtracts.sh ${thismth}

logger -s -t nightlyJob "update the R version of the camera info file"
python << EOD
import fileformats.CameraDetails as cc
s = cc.SiteInfo()
s.saveAsR('${RCODEDIR}/CONFIG/StationList.r')
EOD

logger -s -t nightlyJob "update the annual report for this year"
${SRC}/analysis/monthlyReports.sh ALL ${thisyr} force

logger -s -t nightlyJob "update other relevant showers"
${SRC}/analysis/reportYear.sh ${thisyr}

logger -s -t nightlyJob  "update the data for last month too, since some data comes in quite late"
dom=`date '+%d'`
if [ $dom -lt 10 ] ; then 
    lastmth=`date --date='-1 month' '+%Y%m'`
    lastyr=`date --date='-1 month' '+%Y'`

    ${SRC}/analysis/updateRMSShowerAssocs.sh ${lastmth}
    ${SRC}/website/createMthlyExtracts.sh ${lastmth}
    ${SRC}/website/createShwrExtracts.sh ${lastmth}
fi

logger -s -t nightlyJob "create the cover page for the website"
${SRC}/website/createSummaryTable.sh

logger -s -t nightlyJob "create station status report"
${SRC}/website/cameraStatusReport.sh

logger -s -t nightlyJob "create event log for other networks"
python $SRC/ukmon_pylib/reports/createExchangeFiles.py

logger -s -t nightlyJob "clean up old logs"
find $SRC/logs -name "nightly*" -mtime +7 -exec rm -f {} \;

logger -s -t nightlyJob "Finished"