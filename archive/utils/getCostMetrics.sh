#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# script to get AWS cost metrics for ukmon tagged assets
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

if [ $# -lt 1 ] ; then 
    thismth=`date '+%m'`
else
    thismth=$1
fi

export AWS_DEFAULT_REGION=eu-west-1

cd $DATADIR/costs
    
export AWS_PROFILE=ukmonshared
python $PYLIB/metrics/costMetrics.py $here eu-west-1 $thismth

export AWS_PROFILE=Mark
python $PYLIB/metrics/costMetrics.py $here eu-west-1 $thismth

export AWS_PROFILE=realukms
python $PYLIB/metrics/costMetrics.py $here eu-west-1 $thismth

export AWS_PROFILE=