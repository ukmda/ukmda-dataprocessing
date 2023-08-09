#!/bin/bash

# Copyright (C) 2018- Mark McIntyre

logger -s -t dataSync "RUNTIME $SECONDS start raw data and image sync"

yr=$(date +%Y)
ym=$(date +%Y%m)
ymd=$(date +%Y%m%d)
pyr=$(date -d '-1 day' +%Y)
pym=$(date -d '-1 day' +%Y%m)
pymd=$(date -d '-1 day' +%Y%m%d)

# sync the images, mp4s for todays and yesterdays date. This captures any cameras uploading to the wrong location
logger -s -t dataSync "RUNTIME $SECONDS images and mp4s"
aws s3 sync s3://ukmeteornetworkarchive/img/single/${yr}/${ym}/  s3://ukmda-website/img/single/${yr}/${ym}/ --exclude "*" --include "*${pymd}*" --include "*${ymd}*" --quiet
aws s3 sync s3://ukmeteornetworkarchive/img/mp4/${yr}/${ym}/  s3://ukmda-website/img/mp4/${yr}/${ym}/ --exclude "*" --include "*${pymd}*" --include "*${ymd}*" --quiet
# and for yesterdays date (this does nothing if the dates are in the same month)
aws s3 sync s3://ukmeteornetworkarchive/img/single/${pyr}/${pym}/  s3://ukmda-website/img/single/${pyr}/${pym}/ --exclude "*" --include "*${pymd}*" --include "*${ymd}*" --quiet
aws s3 sync s3://ukmeteornetworkarchive/img/mp4/${pyr}/${pym}/  s3://ukmda-website/img/mp4/${pyr}/${pym}/ --exclude "*" --include "*${pymd}*" --include "*${ymd}*" --quiet

# and sync them the other way too so they're avalable on the main website before the batch runs
# this is necessary because the Lambda that runs in the other account scans for them
aws s3 sync s3://ukmda-website/img/single/${yr}/${ym}/ s3://ukmeteornetworkarchive/img/single/${yr}/${ym}/ --exclude "*" --include "*${pymd}*" --include "*${ymd}*" --quiet
aws s3 sync s3://ukmda-website/img/mp4/${yr}/${ym}/ s3://ukmeteornetworkarchive/img/mp4/${yr}/${ym}/   --exclude "*" --include "*${pymd}*" --include "*${ymd}*" --quiet
# and for yesterdays date
aws s3 sync s3://ukmda-website/img/single/${pyr}/${pym}/ s3://ukmeteornetworkarchive/img/single/${pyr}/${pym}/ --exclude "*" --include "*${pymd}*" --include "*${ymd}*" --quiet
aws s3 sync s3://ukmda-website/img/mp4/${pyr}/${pym}/ s3://ukmeteornetworkarchive/img/mp4/${pyr}/${pym}/  --exclude "*" --include "*${pymd}*" --include "*${ymd}*" --quiet

# sync the platepar.cal files and two sets of KMLs from the other account. We'll sync back later
logger -s -t dataSync "RUNTIME $SECONDS platepars and kmls"
aws s3 sync s3://ukmeteornetworkarchive/img/kmls/  s3://ukmda-website/img/kmls/ --quiet
aws s3 sync s3://ukmon-shared/consolidated/platepars/ s3://ukmda-shared/consolidated/platepars/  --quiet
aws s3 sync s3://ukmon-shared/kmls/ s3://ukmda-shared/kmls/  --quiet

# sync the UFO csv files so they can be consolidated too
aws s3 mv s3://ukmon-shared/consolidated/temp/ s3://ukmda-shared/consolidated/temp/ --recursive --dryrun

# sync the solver data. Loop over locations and cams for scan efficiency
# we will sync the other way AFTER the batch has run, because we don't want to delay the batch unnecessarily
# files are in a folder dated yesterday
logger -s -t dataSync "RUNTIME $SECONDS ftpdetect files"
cams=$(aws s3 ls s3://ukmon-shared/matches/RMSCorrelate/ | grep PRE | awk '{print $2}' | egrep -v "daily|traj|plots|:")
for cam in $cams ; do 
    days=$(aws s3 ls s3://ukmon-shared/matches/RMSCorrelate/${cam} | grep PRE | awk '{print $2}' | egrep -v "daily|traj|plots|:" | grep ${pymd})
    if [ $? == 0 ]; then 
    for day in $days ; do 
            aws s3 sync s3://ukmon-shared/matches/RMSCorrelate/${cam}${day} s3://ukmda-shared/matches/RMSCorrelate/${cam}${day}  --quiet
        done
    fi
done

# sync the other archive data. Loop over locations and cams for scan efficiency
# files are in a folder dated yesterday
logger -s -t dataSync "RUNTIME $SECONDS archive folders"
locs=$(aws s3 ls s3://ukmon-shared/archive/ | grep PRE | awk '{print $2}')
for loc in $locs ; do 
    cams=$(aws s3 ls s3://ukmon-shared/archive/${loc} | grep PRE | awk '{print $2}')
    for cam in $cams ; do 
        aws s3 sync s3://ukmon-shared/archive/${loc}${cam}${pyr}/${pym}/${pymd} s3://ukmda-shared/archive/${loc}${cam}${pyr}/${pym}/${pymd}  --quiet
    done
done
logger -s -t dataSync "RUNTIME $SECONDS done"
