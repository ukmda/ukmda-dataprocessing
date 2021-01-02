#!/bin/bash
# bash script to reduce a month of data
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/orbitsolver.ini > /dev/null 2>&1
ym=$1
yr=${ym:0:4}
mth=${ym:3:2}

ls -1d ${inputs}/${yr}/${ym}/*  | while read i
do
    indir=`basename $i`
    $here/reduceOrbit.sh $indir $2
done
$here/createYearlyOrbitIndex.sh $yr