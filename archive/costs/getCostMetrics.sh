#!/bin/bash
#
# script to get AWS cost metrics for ukmon tagged assets
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

if [ $# -lt 1 ] ; then 
    thismth=`date '+%m'`
else
    thismth=$1
fi

source /home/ec2-user/venvs/${RMS_ENV}/bin/activate
export PYTHONPATH=$wmpl_loc:$PYLIB
export AWS_DEFAULT_REGION=eu-west-1

cd $SRC/metrics

source ~/.ssh/marks-keys
python $PYLIB/metrics/costMetrics.py $here eu-west-1 $thismth