#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1
source ~/venvs/$RMS_ENV/bin/activate
if [ $# -lt 1 ] ; then
    yr=$(date +%Y)
else
    yr=$1
fi
mth=$(date +%m)

if [ $yr -lt 2018 ] ; then
    singlf=$RCODEDIR/DATA/consolidated/M_$yr-consolidated.csv
else
    singlf=$RCODEDIR/DATA/consolidated/UKMON-$yr-single.csv
fi

livef=idx$yr}01.csv

mkdir -p $RCODEDIR/DATA/searchidx
echo python ufoToSearchableFormat.py $CONFIG/config.ini $singlef $livef $RCODEDIR/DATA/searchidx