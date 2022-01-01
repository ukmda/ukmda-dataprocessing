#!/bin/bash
#
# bash to get list of stations excluded from analysis
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1
export SRC DATADIR
source ~/venvs/$WMPL_ENV/bin/activate
export PYTHONPATH=$PYLIB:$wmpl_loc

rsync -avz ~/ukmon-shared/admin $DATADIR/

source ~/.ssh/ukmon-markmcintyre-keys
export AWS_DEFAULT_REGION=eu-west-2
python $PYLIB/reports/reportBadCameras.py 3


#uxt=$(date -d 'yesterday' +%s000)
#js=$(aws logs filter-log-events --log-group-name "/aws/lambda/consolidateFTPdetect" --start-time $uxt --filter-pattern "too many")
#echo $js | jq '.events | .[] | .message'
