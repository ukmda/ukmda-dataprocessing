#!/bin/bash
# bash script to reduce a month of data
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/orbitsolver.ini > /dev/null 2>&1
ym=$1
yr=${ym:0:4}

ls -1d ${inputs}/${yr}/${ym}/*  | while read i
do
    $here/reduceOrbit.sh $i
done
