#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1

YYMMDD=20220120

basepth=~/dev/data/RMSCorrelate
mkdir $basepth

fldrs=$(aws s3 ls s3://ukmda-shared/matches/RMSCorrelate/ | egrep "UK|BE|IE" | awk '{print $2}')

for fldr in $fldrs ; do
    camid=${fldr:0:6}
    aws s3 sync s3://ukmda-shared/matches/RMSCorrelate/${fldr} ${basepth}/${fldr} --exclude "*" --include "${camid}_${YYMMDD}*"    
done 
