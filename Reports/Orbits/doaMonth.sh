#!/bin/bash
# bash script to reduce a month of data
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
if [[ "$here" == *"prod"* ]] ; then
    echo sourcing prod config
    source $HOME/prod/config/config.ini >/dev/null 2>&1
else
    echo sourcing dev config
    source $HOME/src/config/config.ini >/dev/null 2>&1
fi

ym=$1
yr=${ym:0:4}
mth=${ym:3:2}

ls -1d ${MATCHDIR}/${yr}/${ym}/*  | while read i
do
    indir=`basename $i`
    $here/doOneMatch.sh $indir $2
done
$SRC/website/createPageIndex.sh $ym

