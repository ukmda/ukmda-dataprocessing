#!/bin/bash
#
# script to update match data each night and then recalc any necessary orbits

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

thismth=`date '+%Y%m'`
$here/../matches/findAllMatches.sh $thismth
$here/../orbits/doaMonth.sh $thismth
dom=`date '+%d'`
if [ $dom -lt 10 ] ; then 
    lastmth=`date --date='-1 month' '+%Y%m'`
    $here/../matches/findAllMatches.sh $lastmth
    $here/../orbits/doaMonth.sh $lastmth
else
    echo "create monthly report here"
fi
thisyr=`date '+%Y'`
$here/../analysis/monthlyReports.sh ALL ${thisyr} force
$here/../website/createSummaryTable.sh
