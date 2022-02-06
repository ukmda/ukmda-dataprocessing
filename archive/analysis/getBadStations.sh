#!/bin/bash
#
# bash to get list of stations excluded from analysis
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1
source ~/venvs/$WMPL_ENV/bin/activate

rsync -avz ~/ukmon-shared/admin $DATADIR/

source ~/.ssh/ukmon-markmcintyre-keys
export AWS_DEFAULT_REGION=eu-west-2
python -m reports.reportBadCameras 3
