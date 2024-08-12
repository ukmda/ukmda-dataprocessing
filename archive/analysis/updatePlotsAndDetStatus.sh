#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# Rerun the process that creates consolidated plots vs solar longitude 
# and updates the database of single detection statuses
#
# Consumes
#   All single-station data
#   All trajectory pickles for the last MATCHSTART days
#
# Produces
#   Updates the Charts and the database of single stations showing whether a detection was matched
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration
source $here/../config.ini >/dev/null 2>&1

# logstream name inherited from parent environment but set it if not
if [ "$NJLOGSTREAM" == "" ]; then
    NJLOGSTREAM=$(date +%Y%m%d-%H%M%S)
    aws logs create-log-stream --log-group-name $NJLOGGRP --log-stream-name $NJLOGSTREAM --profile ukmonshared
fi
log2cw $NJLOGGRP $NJLOGSTREAM "starting updatePlotsAndDetStatus" updatePlotsAndDetStatus

# set the profile to the EE account so we can run the server and monitor progress
export AWS_PROFILE=ukmonshared

if [ $# -gt 0 ] ; then
    if [ "$1" != "" ] ; then
        log2cw $NJLOGGRP $NJLOGSTREAM "selecting range" updatePlotsAndDetStatus
        MATCHSTART=$1
    fi
    if [ "$2" != "" ] ; then
        MATCHEND=$2
    else
        log2cw $NJLOGGRP $NJLOGSTREAM "matchend was not supplied, using 2 days" updatePlotsAndDetStatus
        MATCHEND=$(( $MATCHSTART - 2 ))
    fi
fi
begdate=$(date --date="-$MATCHSTART days" '+%Y%m%d')
rundate=$(date --date="-$MATCHEND days" '+%Y%m%d')

log2cw $NJLOGGRP $NJLOGSTREAM "start correlation server" updatePlotsAndDetStatus
stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
if [ $stat -eq 80 ]; then 
    aws ec2 start-instances --instance-ids $SERVERINSTANCEID
fi
log2cw $NJLOGGRP $NJLOGSTREAM "start correlation server" updatePlotsAndDetStatus
while [ "$stat" -ne 16 ]; do
    sleep 5
    log2cw $NJLOGGRP $NJLOGSTREAM "checking server status" updatePlotsAndDetStatus
    stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
done
log2cw $NJLOGGRP $NJLOGSTREAM "updating plots etc for dates ${begdate} to ${rundate}" updatePlotsAndDetStatus
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

log2cw $NJLOGGRP $NJLOGSTREAM "creating the run script" updatePlotsAndDetStatus
execrerun=execreplot.sh
execrerunsh=/tmp/$execrerun
python -c "from traj.createDistribMatchingSh import createExecReplotSh;createExecReplotSh($MATCHSTART, $MATCHEND, '$execrerunsh')"
chmod +x $execrerunsh

log2cw $NJLOGGRP $NJLOGSTREAM "get server details" updatePlotsAndDetStatus
privip=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].PrivateIpAddress --output text)
while [ "$privip" == "" ] ; do
    sleep 5
    log2cw $NJLOGGRP $NJLOGSTREAM "getting IP address" updatePlotsAndDetStatus
    privip=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].PrivateIpAddress --output text)
done

log2cw $NJLOGGRP $NJLOGSTREAM "deploy the script to the server $privip and run it" updatePlotsAndDetStatus

scp -i $SERVERSSHKEY $execrerunsh ec2-user@$privip:data/distrib/$execrerun
while [ $? -ne 0 ] ; do
    # in case the server isn't responding to ssh sessions yet
    sleep 10
    log2cw $NJLOGGRP $NJLOGSTREAM "server not responding yet, retrying" updatePlotsAndDetStatus
    scp -i $SERVERSSHKEY $execrerunsh ec2-user@$privip:data/distrib/$execrerun
done 
# push the python and templates required
rsync -avz  -e "ssh -i $SERVERSSHKEY" $PYLIB/traj/pickleAnalyser.py ec2-user@$privip:src/ukmon_pylib/traj

# now run the script
ssh -i $SERVERSSHKEY ec2-user@$privip "data/distrib/$execrerun"

log2cw $NJLOGGRP $NJLOGSTREAM "job run, stop the server again" updatePlotsAndDetStatus
aws ec2 stop-instances --instance-ids $SERVERINSTANCEID

log2cw $NJLOGGRP $NJLOGSTREAM "get a list of uncalibrated data" updatePlotsAndDetStatus
aws s3 sync $UKMONSHAREDBUCKET/matches/consumed/ $DATADIR/single/used/ --exclude "*" --include "*.txt" --quiet
rundate=$(cat $DATADIR/rundate.txt)
python -c "from analysis.gatherDetectionData import getUncalibratedImageList;getUncalibratedImageList('$rundate');"

# and then clear the profile again
unset AWS_PROFILE
# refresh the website index pages just in case any new data
dailyrep=$(ls -1tr $DATADIR/dailyreports/20* | tail -1)
$SRC/website/updateIndexPages.sh $dailyrep

log2cw $NJLOGGRP $NJLOGSTREAM "finished updatePlotsAndDetStatus" updatePlotsAndDetStatus
