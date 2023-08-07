#!/bin/bash

# Copyright (C) 2018- Mark McIntyre

logger -s -t dataSyncBack "RUNTIME $SECONDS start raw data sync back"
# data is in folders with yesterdays date
yr=$(date -d '-1 day' +%Y)
ym=$(date -d '-1 day' +%Y%m)
ymd=$(date -d '-1 day' +%Y%m%d)

# sync the raw data back from the new account to the old. 
# this is so that both sites have a copy. This will push everything since we synced the other way earlier 
aws s3 sync s3://ukmda-website/img/kmls/ s3://ukmeteornetworkarchive/img/kmls/  --quiet
aws s3 sync s3://ukmda-shared/consolidated/platepars/ s3://ukmon-shared/consolidated/platepars/ --quiet
aws s3 sync s3://ukmda-shared/kmls/ s3://ukmon-shared/kmls/  --quiet

cams=$(aws s3 ls s3://ukmda-shared/matches/RMSCorrelate/ | grep PRE | awk '{print $2}' | egrep -v "daily|traj|plots|:")
for cam in $cams ; do 
    days=$(aws s3 ls s3://ukmda-shared/matches/RMSCorrelate/${cam} | grep PRE | awk '{print $2}' | egrep -v "daily|traj|plots|:" | grep ${ymd})
    if [ $? == 0 ]; then 
        aws s3 sync s3://ukmda-shared/matches/RMSCorrelate/${cam}${days} s3://ukmon-shared/matches/RMSCorrelate/${cam}${days}  --quiet
    fi
done

# sync the other archive data. Loop over locations and cams for scan efficiency as we only want the most recent data
locs=$(aws s3 ls s3://ukmda-shared/archive/ | awk '{print $2}')
for loc in $locs ; do 
    cams=$(aws s3 ls s3://ukmda-shared/archive/${loc} | awk '{print $2}')
    for cam in $cams ; do 
        aws s3 sync s3://ukmda-shared/archive/${loc}${cam}${yr}/${ym}/${ymd} s3://ukmon-shared/archive/${loc}${cam}${yr}/${ym}/${ymd} --quiet
    done
done
logger -s -t dataSyncBack "RUNTIME $SECONDS done"
