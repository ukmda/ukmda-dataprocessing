#!/bin/bash
#
# script to update match data each night and then recalc any necessary orbits

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $HOME/src/config/config.ini > /dev/null 2>&1

thismth=`date '+%Y%m'`
thismth=`date '+%Y'`

${SRC}/matches/findAllMatches.sh $thismth
${SRC}/orbits/doaMonth.sh $thismth
${SRC}/website/createOrbitIndex.sh $thismth
${SRC}/website/createOrbitIndex.sh $thisyr
${SRC}/analysis/updateRMSShowerAssocs.sh ${thismth}

dom=`date '+%d'`
if [ $dom -lt 10 ] ; then 
    lastmth=`date --date='-1 month' '+%Y%m'`
    lastyr=`date --date='-1 month' '+%Y'`

    ${SRC}/matches/findAllMatches.sh $lastmth
    ${SRC}/orbits/doaMonth.sh $lastmth
    ${SRC}/website/createOrbitIndex.sh $lastmth
    ${SRC}/website/createOrbitIndex.sh $lastyr
    ${SRC}/analysis/updateRMSShowerAssocs.sh ${lastmth}
else
    echo "create monthly report here"
fi
thisyr=`date '+%Y'`
${SRC}/analysis/monthlyReports.sh ALL ${thisyr} force
${SRC}/website/createSummaryTable.sh
