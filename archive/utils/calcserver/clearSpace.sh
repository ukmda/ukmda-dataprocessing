#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# script to backup then clear down orbits from the local disk. 

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source ~/config/config.ini >/dev/null 2>&1
export AWS_PROFILE=ukmonshared

if [ "$(hostname)" != "ukmcalcserver" ] ; then
    echo "wrong server"
    exit
fi 

thisyr=$(date +%Y)
thismth=$(date +%Y%m)
lastmth=$(date +%Y%m -d 'last month')
twomth=$(date +%Y%m -d '-2 month')
lastyr=${twomth:0:4}

df .

# purge trajectory folders of old PNGs. These aren't required here, and have already been pushed to the Web bucket
pushd ~/ukmon-shared/matches/RMSCorrelate/trajectories/$thisyr
mths=$(ls -1d ${thisyr}*)
for mth in $mths ; do 
    if [[ $mth != $lastmth && $mth != $thismth ]] ; then 
        echo purging $mth 
        find $mth -name "$thisyr*.png" -exec rm -f {} \;
    fi 
done
if [ $lastyr != $thisyr ] ; then
    pushd ../$lastyr
    echo purging $twomth
    find $twomth -name "$lastyr*.png" -exec rm -f {} \;
    popd
fi 
popd
#purge the raw data folders of old raw data - this is all over on the S3 store if needed
pushd ~/ukmon-shared/matches/RMSCorrelate
targdirs=$(ls -1 | egrep -v "traj|daily|test|plot|proce|candi")
for td in $targdirs ; do
    find $td -mtime +90 -exec rm -Rf {} \; 
done
df .
popd
