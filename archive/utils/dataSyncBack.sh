#!/bin/bash

# Copyright (C) 2018- Mark McIntyre

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

# done with the ftptoukmon lambda in the MDA account
#cams=$(aws s3 ls s3://ukmda-shared/matches/RMSCorrelate/ | grep PRE | awk '{print $2}' | egrep -v "daily|traj|plots|:")
#for cam in $cams ; do 
#    days=$(aws s3 ls s3://ukmda-shared/matches/RMSCorrelate/${cam} | grep PRE | awk '{print $2}' | egrep -v "daily|traj|plots|:" | grep ${pymd})
#    if [ $? == 0 ]; then 
#        for day in $days ; do 
#            aws s3 sync s3://ukmda-shared/matches/RMSCorrelate/${cam}${day} s3://ukmon-shared/matches/RMSCorrelate/${cam}${day}  --quiet
#        done
#    fi
#done

# sync the other archive data. Loop over locations and cams for scan efficiency as we only want the most recent data
logger -s -t dataSyncBack "RUNTIME $SECONDS calib, flux, and other reports"
locs=$(aws s3 ls s3://ukmda-shared/archive/ | grep PRE | awk '{print $2}')
for loc in $locs ; do 
    cams=$(aws s3 ls s3://ukmda-shared/archive/${loc} | grep PRE | awk '{print $2}')
    for cam in $cams ; do 
        aws s3 sync s3://ukmda-shared/archive/${loc}${cam}${pyr}/${pym}/${pymd} s3://ukmon-shared/archive/${loc}${cam}${pyr}/${pym}/${pymd} --quiet --exclude "FF*" --exclude "fl*" --exclude "pla*"
    done
done
logger -s -t dataSyncBack "RUNTIME $SECONDS done"
