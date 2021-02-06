#!/bin/bash
#
# Script to call reduceOrbit and then move the results as needed 
# for the archive website
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the helper functions
source $HOME/src/config/config.ini > /dev/null 2>&1

${SRC}/orbits/doOneMatch.sh $1 force

ym=$(date +%Y%m)
$src/website/createPageIndex.sh $ym
yr=$(date +%Y)
$src/website/createPageIndex.sh $yr