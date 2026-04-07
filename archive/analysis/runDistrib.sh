#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# Run the distributed solver
#
# Parameters
#   [int] (optional) days ago to run for
#   [int] (optional) days to check
# for example passing in 2 and 3 will run for two days ago, and scan three days of data for updates
#
# Consumes
#   All single-station data
#
# Produces
#   Solved trajectories
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration
source $here/../config.ini >/dev/null 2>&1

 [ "$RUNTIME_ENV" == "DEV" ] && TESTMODE="true"
 [ "$RUNTIME_ENV" == "DEV" ] && TESTSUFF="/test"

# logstream name inherited from parent environment but set it if not
if [ "$NJLOGSTREAM" == "" ]; then
    NJLOGSTREAM=$(date +%Y%m%d-%H%M%S)
    aws logs create-log-stream --log-group-name $NJLOGGRP --log-stream-name $NJLOGSTREAM --profile ukmonshared
fi
log2cw $NJLOGGRP $NJLOGSTREAM "starting runDistrib" runDistrib

# set the profile to the UKMDA account so we can run the server and monitor progress
export AWS_PROFILE=ukmonshared

if [ $# -gt 0 ] ; then
    if [ "$1" != "" ] ; then
        log2cw $NJLOGGRP $NJLOGSTREAM "selecting range" runDistrib
        MATCHSTART=$1
    fi
    if [ "$2" != "" ] ; then
        MATCHEND=$2
    else
        log2cw $NJLOGGRP $NJLOGSTREAM "matchend was not supplied, using 2 days" runDistrib
        MATCHEND=$(( $MATCHSTART - 2 ))
    fi
fi
begdate=$(date --date="-$MATCHSTART days" '+%Y%m%d')
rundate=$(date --date="-$MATCHEND days" '+%Y%m%d')

log2cw $NJLOGGRP $NJLOGSTREAM "start correlation server" runDistrib
stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
if [ $stat -eq 80 ]; then 
    aws ec2 start-instances --instance-ids $SERVERINSTANCEID
fi

while [ "$stat" -ne 16 ]; do
    sleep 5
    log2cw $NJLOGGRP $NJLOGSTREAM "checking server status" runDistrib
    stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
done

log2cw $NJLOGGRP $NJLOGSTREAM "running phase 1 for dates ${begdate} to ${rundate}" runDistrib

conda activate $HOME/miniconda3/envs/${WMPL_ENV}

log2cw $NJLOGGRP $NJLOGSTREAM "creating the run script" runDistrib
execdist=execdistrib.sh
execMatchingsh=/tmp/$execdist
python -m traj.createDistribMatchingSh $MATCHSTART $MATCHEND $execMatchingsh $TESTMODE
chmod +x $execMatchingsh

log2cw $NJLOGGRP $NJLOGSTREAM "get server details" runDistrib
privip=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].PrivateIpAddress --output text)
while [ "$privip" == "" ] ; do
    sleep 5
    log2cw $NJLOGGRP $NJLOGSTREAM "getting IP address" runDistrib
    privip=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].PrivateIpAddress --output text)
done

log2cw $NJLOGGRP $NJLOGSTREAM "deploy the script to the server $privip and run it" runDistrib

scp -i $SERVERSSHKEY $execMatchingsh $SERVERUSERID@$privip:data/distrib/$execdist
while [ $? -ne 0 ] ; do
    # in case the server isn't responding to ssh sessions yet
    sleep 10
    log2cw $NJLOGGRP $NJLOGSTREAM "server not responding yet, retrying" runDistrib
    scp -i $SERVERSSHKEY $execMatchingsh $SERVERUSERID@$privip:data/distrib/$execdist
done 
# push the python code and ECS templates required
rsync -avz  -e "ssh -i $SERVERSSHKEY" $PYLIB/traj/clusdetails-* $SERVERUSERID@$privip:src/ukmon_pylib/traj
rsync -avz  -e "ssh -i $SERVERSSHKEY" $PYLIB/traj/taskrunner*.json $SERVERUSERID@$privip:src/ukmon_pylib/traj
rsync -avz  -e "ssh -i $SERVERSSHKEY" $PYLIB/traj/consolidateDistTraj.py $SERVERUSERID@$privip:src/ukmon_pylib/traj
rsync -avz  -e "ssh -i $SERVERSSHKEY" $PYLIB/traj/distributeCandidates.py $SERVERUSERID@$privip:src/ukmon_pylib/traj
rsync -avz  -e "ssh -i $SERVERSSHKEY" $PYLIB/traj/pickleAnalyser.py $SERVERUSERID@$privip:src/ukmon_pylib/traj

# now run the script
log2cw $NJLOGGRP $NJLOGSTREAM "start distributed processing" runDistrib
ssh -i $SERVERSSHKEY $SERVERUSERID@$privip "data/distrib/$execdist"

log2cw $NJLOGGRP $NJLOGSTREAM "job run, stop the server again" runDistrib
aws ec2 stop-instances --instance-ids $SERVERINSTANCEID

log2cw $NJLOGGRP $NJLOGSTREAM "monitoring and waiting for completion" runDistrib

python -c "from traj.distributeCandidates import monitorProgress as mp; mp('${rundate}', '${TESTMODE}'); "

mkdir -p $DATADIR/distrib
cd $DATADIR/distrib

log2cw $NJLOGGRP $NJLOGSTREAM "restarting server to consolidate results" runDistrib
stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
if [ $stat -eq 80 ]; then 
    aws ec2 start-instances --instance-ids $SERVERINSTANCEID
fi
log2cw $NJLOGGRP $NJLOGSTREAM "waiting for the server to be ready" runDistrib
while [ "$stat" -ne 16 ]; do
    sleep 30
    if [ $stat -eq 80 ]; then 
        aws ec2 start-instances --instance-ids $SERVERINSTANCEID
    fi
    log2cw $NJLOGGRP $NJLOGSTREAM "checking - status is ${stat}" runDistrib
    stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
done

execcons=execconsol.sh
execConsolsh=/tmp/$execcons
python -c "from traj.createDistribMatchingSh import createExecConsolSh;createExecConsolSh($MATCHSTART, $MATCHEND, '$execConsolsh', '$TESTMODE')"
chmod +x $execConsolsh

log2cw $NJLOGGRP $NJLOGSTREAM "running consolidation" runDistrib
scp -i $SERVERSSHKEY $execConsolsh $SERVERUSERID@$privip:data/distrib/$execcons
ssh -i $SERVERSSHKEY $SERVERUSERID@$privip "data/distrib/$execcons"

log2cw $NJLOGGRP $NJLOGSTREAM "finished consolidation" runDistrib
rsync -avz -e "ssh -i $SERVERSSHKEY" $SERVERUSERID@$privip:ukmon-shared/matches/RMSCorrelate/dbs${TESTSUFF}/*.db $DATADIR/distrib

# remote temporary files
ssh -i $SERVERSSHKEY $SERVERUSERID@$privip "find /tmp -maxdepth 1 -name "*.pickle"  -mtime +7 -exec rm -f {} \;"

log2cw $NJLOGGRP $NJLOGSTREAM "stopping calcserver again" runDistrib
aws ec2 stop-instances --instance-ids $SERVERINSTANCEID

# grab a copy of the indvidual container trajectory dbs so we can get a list of new solutions
rm -Rf $DATADIR/latest/dbs/
aws s3 sync $UKMONSHAREDBUCKET/matches/distrib${TESTSUFF}/ $DATADIR/latest/dbs/ --exclude "*" --include "traj*.db" --quiet

log2cw $NJLOGGRP $NJLOGSTREAM "compressing the processed data" runDistrib
tar czvf $DATADIR/distrib/databases_${rundate}.tgz $DATADIR/distrib/*.db
aws s3 mv $UKMONSHAREDBUCKET/matches/distrib${TESTSUFF}/${rundate}.pickle $DATADIR/distrib --quiet
tar czvf $DATADIR/distrib/${rundate}.tgz $DATADIR/distrib/${rundate}*.json $DATADIR/distrib/${rundate}.pickle
aws s3 cp $DATADIR/distrib/${rundate}.tgz $UKMONSHAREDBUCKET/matches/distrib${TESTSUFF}/done/ --quiet
rm -f $DATADIR/distrib/${rundate}*.json $DATADIR/distrib/${rundate}.pickle
aws s3 rm $UKMONSHAREDBUCKET/matches/distrib${TESTSUFF}/ --exclude "*" --include "*.db" --exclude "test/*" --exclude "dbs/*" --recursive --quiet

# and then clear the profile again
unset AWS_PROFILE
log2cw $NJLOGGRP $NJLOGSTREAM "finished runDistrib" runDistrib
