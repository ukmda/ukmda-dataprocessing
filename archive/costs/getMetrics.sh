#!/bin/bash
#
# script to get AWS logs for ukmon data
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

thismth=`date '+%Y%m'`
thisyr=`date '+%Y'`

source /home/ec2-user/venvs/${RMS_ENV}/bin/activate
export PYTHONPATH=$wmpl_loc:$PYLIB
export AWS_DEFAULT_REGION=eu-west-1

cd $SRC/metrics

source ~/.ssh/marks-keys
python $PYLIB/metrics/getMetrics.py $here eu-west-1
#python $PYLIB/metrics/getMetrics.py $here eu-west-2
