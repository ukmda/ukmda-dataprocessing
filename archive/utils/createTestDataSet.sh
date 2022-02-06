#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

YYMMDD=20220120

basepth=~/dev/data/RMSCorrelate
mkdir $basepth

cd $MATCHDIR/RMSCorrelate
ls -1d UK*/*${YYYYMMDD}* | while read i ; do 
    mkdir -p $basepth/$i
    cp $i/* $basepth/$i
done
