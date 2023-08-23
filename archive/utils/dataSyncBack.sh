#!/bin/bash

# Copyright (C) 2018- Mark McIntyre

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1

logger -s -t dataSyncBack "RUNTIME $SECONDS start raw data sync back"
# data is in folders with yesterdays date
pyr=$(date -d '-1 day' +%Y)
pym=$(date -d '-1 day' +%Y%m)
pymd=$(date -d '-1 day' +%Y%m%d)

# sync the raw data back from the new account to the old. 
# this is so that both sites have a copy. This will push everything since we synced the other way earlier 
logger -s -t dataSyncBack "RUNTIME $SECONDS kmls and platepars"
aws s3 sync s3://ukmda-website/img/kmls/ s3://ukmeteornetworkarchive/img/kmls/  --quiet
aws s3 sync s3://ukmda-shared/consolidated/platepars/ s3://ukmon-shared/consolidated/platepars/ --quiet
aws s3 sync s3://ukmda-shared/kmls/ s3://ukmon-shared/kmls/  --quiet

logger -s -t dataSyncBack "RUNTIME $SECONDS done"
