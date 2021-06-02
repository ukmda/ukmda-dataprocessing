#!/bin/bash
#
# script to get AWS logs for ukmon data
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

thismth=`date '+%Y%m'`
thisyr=`date '+%Y'`

source $WEBSITEKEY
source ${RMS_LOC}/bin/activate
export AWS_DEFAULT_REGION=eu-west-2

cd $SRC/metrics
export PYTHONPATH=$wmpl_loc:$PYLIB

python $PYLIB/metrics/getMetrics.py
