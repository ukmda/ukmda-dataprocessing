#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# bash to get list of stations excluded from analysis
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
source ~/venvs/$WMPL_ENV/bin/activate

logger -s -t getBadStations "starting"
aws s3 sync $UKMONSHAREDBUCKET/admin  $DATADIR/admin --dryrun --quiet 

python -m reports.reportBadCameras 3
logger -s -t getBadStations "finished"
