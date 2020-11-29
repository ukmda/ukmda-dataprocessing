#!/bin/bash
#
# script to update match data each night and then recalc any necessary orbits

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

thismth=`date '+%Y%m'
echo $here/../matches/findAllMatches.sh $thismth
dom=`date '+%d'`
if [ $dom -lt 10 ] ; then 
    lastmth=`date --date='-1 month' '+%Y%m'`
    echo $here/../matches/findAllMatches.sh $lastmth
fi