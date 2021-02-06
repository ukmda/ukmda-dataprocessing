#!/bin/bash
# bash script to reduce a month of data
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $HOME/src/config/config.ini > /dev/null 2>&1

ym=$1
yr=${ym:0:4}
mth=${ym:3:2}

ls -1d ${MATCHDIR}/${yr}/${ym}/*  | while read i
do
    indir=`basename $i`
    $here/doOneMatch.sh $indir $2
done
$src/website/createPageIndex.sh $ym

