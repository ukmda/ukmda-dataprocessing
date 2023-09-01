#!/bin/bash

# Copyright (C) 2018- Mark McIntyre

logger -s -t dataSync "RUNTIME $SECONDS start raw data and image sync"

yr=$(date +%Y)
ym=$(date +%Y%m)
ymd=$(date +%Y%m%d)
pyr=$(date -d '-1 day' +%Y)
pym=$(date -d '-1 day' +%Y%m)
pymd=$(date -d '-1 day' +%Y%m%d)

# The main purpose of this script is to sync data from the OLD share to the NEW one. 
# Data will typically be on the old share because the toolset is out of date. Eventually this script will do nothong. 
# Note that we don't need to sync the other way because its done by lambda functions and bucket triggers

# NOTE: I'm using the --size-only parameter to avoid copying based on datestamp. This is necessary because as data
# is uploaded by the cameras, lambdas replicate it across to the ukmon shares. This alters the timestamp in the target
# and so the new files would be copied back again by the code below - and this would trigger the Lambda to replicate them again! 

# sync the images, mp4s for todays and yesterdays date. 
logger -s -t dataSync "RUNTIME $SECONDS images and mp4s"
aws s3 sync s3://ukmeteornetworkarchive/img/single/${yr}/${ym}/  s3://ukmda-website/img/single/${yr}/${ym}/ --exclude "*" --include "*${pymd}*" --include "*${ymd}*" --size-only  --quiet
aws s3 sync s3://ukmeteornetworkarchive/img/mp4/${yr}/${ym}/  s3://ukmda-website/img/mp4/${yr}/${ym}/ --exclude "*" --include "*${pymd}*" --include "*${ymd}*" --size-only --quiet
if [ "$pym" -ne "$ym " ] ; then 
    logger -s -t dataSync "RUNTIME $SECONDS prev mth images and mp4s"
    aws s3 sync s3://ukmeteornetworkarchive/img/single/${pyr}/${pym}/  s3://ukmda-website/img/single/${pyr}/${pym}/ --exclude "*" --include "*${pymd}*" --include "*${ymd}*" --size-only --quiet
    aws s3 sync s3://ukmeteornetworkarchive/img/mp4/${pyr}/${pym}/  s3://ukmda-website/img/mp4/${pyr}/${pym}/ --exclude "*" --include "*${pymd}*" --include "*${ymd}*" --size-only --quiet
fi 

# sync the platepar.cal files and two sets of KMLs from the other account. 
logger -s -t dataSync "RUNTIME $SECONDS platepars and kmls"
aws s3 sync s3://ukmeteornetworkarchive/img/kmls/  s3://ukmda-website/img/kmls/ --size-only --quiet
aws s3 sync s3://ukmon-shared/consolidated/platepars/ s3://ukmda-shared/consolidated/platepars/  --size-only  --quiet
aws s3 sync s3://ukmon-shared/kmls/ s3://ukmda-shared/kmls/  --size-only --quiet

# sync the solver data, in case any is still being sent to the old share. 
# Loop over locations and cams for scan efficiency
logger -s -t dataSync "RUNTIME $SECONDS ftpdetect files"
cams=$(aws s3 ls s3://ukmon-shared/matches/RMSCorrelate/ | grep PRE | awk '{print $2}' | egrep -v "daily|traj|plots|:")
for cam in $cams ; do 
    days=$(aws s3 ls s3://ukmon-shared/matches/RMSCorrelate/${cam} | grep PRE | awk '{print $2}' | egrep -v "daily|traj|plots|:" | grep ${pymd})
    if [ $? == 0 ]; then 
    for day in $days ; do 
            aws s3 sync s3://ukmon-shared/matches/RMSCorrelate/${cam}${day} s3://ukmda-shared/matches/RMSCorrelate/${cam}${day} --size-only
        done
    fi
done

# sync the other archive data. Loop over locations and cams for scan efficiency.
# Note that files are in a folder dated yesterday
logger -s -t dataSync "RUNTIME $SECONDS archive folders"
locs=$(aws s3 ls s3://ukmon-shared/archive/ | grep PRE | awk '{print $2}')
for loc in $locs ; do 
    cams=$(aws s3 ls s3://ukmon-shared/archive/${loc} | grep PRE | awk '{print $2}')
    for cam in $cams ; do 
        aws s3 sync s3://ukmon-shared/archive/${loc}${cam}${pyr}/${pym}/${pymd} s3://ukmda-shared/archive/${loc}${cam}${pyr}/${pym}/${pymd}  --size-only
    done
done
logger -s -t dataSync "RUNTIME $SECONDS done"
