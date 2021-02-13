#!/bin/bash
#
# Script to call reduceOrbit and then move the results as needed 
# for the archive website
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
if [[ "$here" == *"prod"* ]] ; then
    source $HOME/prod/config/config.ini >/dev/null 2>&1
else
    source $HOME/src/config/config.ini >/dev/null 2>&1
fi

${SRC}/orbits/doOneMatch.sh $1 force

ym=$(date +%Y%m)
${SRC}/website/createPageIndex.sh $ym
yr=$(date +%Y)
${SRC}/website/createPageIndex.sh $yr