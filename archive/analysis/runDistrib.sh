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
logger -s -t runDistrib "RUNTIME $SECONDS starting runDistrib"

# load the configuration
source $here/../config.ini >/dev/null 2>&1

# set the profile to the EE account so we can run the server and monitor progress
export AWS_PROFILE=ukmonshared

if [ $# -gt 0 ] ; then
    if [ "$1" != "" ] ; then
        echo "selecting range"
        MATCHSTART=$1
    fi
    if [ "$2" != "" ] ; then
        MATCHEND=$2
    else
        echo "matchend was not supplied, using 2"
        MATCHEND=$(( $MATCHSTART - 2 ))
    fi
fi
begdate=$(date --date="-$MATCHSTART days" '+%Y%m%d')
rundate=$(date --date="-$MATCHEND days" '+%Y%m%d')

logger -s -t runDistrib "RUNTIME $SECONDS start correlation server"
stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
if [ $stat -eq 80 ]; then 
    aws ec2 start-instances --instance-ids $SERVERINSTANCEID
fi
logger -s -t runDistrib "RUNTIME $SECONDS wait for correlation server"
while [ "$stat" -ne 16 ]; do
    sleep 5
    echo "checking"
    stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
done
logger -s -t runDistrib "RUNTIME $SECONDS running phase 1 for dates ${begdate} to ${rundate}"
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

logger -s -t runDistrib "RUNTIME $SECONDS creating the run script"
execMatchingsh=/tmp/execdistrib.sh
python -m traj.createDistribMatchingSh $MATCHSTART $MATCHEND $execMatchingsh
chmod +x $execMatchingsh

logger -s -t runDistrib "RUNTIME $SECONDS get server details"
privip=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].PrivateIpAddress --output text)
while [ "$privip" == "" ] ; do
    sleep 5
    echo "getting ipaddress"
    privip=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].PrivateIpAddress --output text)
done

logger -s -t runDistrib "RUNTIME $SECONDS deploy the script to the server and run it"

scp -i $SERVERSSHKEY $execMatchingsh ec2-user@$privip:/tmp
while [ $? -ne 0 ] ; do
    # in case the server isn't responding to ssh sessions yet
    sleep 10
    echo "server not responding yet, retrying"
    scp -i $SERVERSSHKEY $execMatchingsh ec2-user@$privip:/tmp
done 
# push the python and templates required
rsync -avz  -e "ssh -i $SERVERSSHKEY" $PYLIB/traj/clusdetails-* ec2-user@$privip:src/ukmon_pylib/traj
rsync -avz  -e "ssh -i $SERVERSSHKEY" $PYLIB/traj/taskrunner.json ec2-user@$privip:src/ukmon_pylib/traj
rsync -avz  -e "ssh -i $SERVERSSHKEY" $PYLIB/traj/consolidateDistTraj.py ec2-user@$privip:src/ukmon_pylib/traj
rsync -avz  -e "ssh -i $SERVERSSHKEY" $PYLIB/traj/distributeCandidates.py ec2-user@$privip:src/ukmon_pylib/traj

# now run the script
ssh -i $SERVERSSHKEY ec2-user@$privip $execMatchingsh

logger -s -t runDistrib "RUNTIME $SECONDS job run, stop the server again"
aws ec2 stop-instances --instance-ids $SERVERINSTANCEID

logger -s -t runDistrib "RUNTIME $SECONDS monitoring and waiting for completion"

python -c "from traj.distributeCandidates import monitorProgress as mp; mp('${rundate}'); "

logger -s -t runDistrib "RUNTIME $SECONDS merging in the new json files"
mkdir -p $DATADIR/distrib
cd $DATADIR/distrib

# make sure the database isn't corrupt before overwriting it !! 
if [ -s $DATADIR/distrib/processed_trajectories.json ] ; then 
    aws s3 sync $UKMONSHAREDBUCKET/matches/distrib/ $DATADIR/distrib/ --exclude "*" --include "*.json" --quiet
    cp -f $DATADIR/distrib/processed_trajectories.json $DATADIR/distrib/prev_processed_trajectories.json

    numtoconsol=$(ls -1 $DATADIR/distrib/${rundate}*.json | wc -l)
    if [ $numtoconsol -gt 5 ] ; then 
        logger -s -t runDistrib "RUNTIME $SECONDS restarting calcserver to consolidate results"
        stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
        if [ $stat -eq 80 ]; then 
            aws ec2 start-instances --instance-ids $SERVERINSTANCEID
        fi
        logger -s -t runDistrib "RUNTIME $SECONDS waiting for the server to be ready"
        while [ "$stat" -ne 16 ]; do
            sleep 30
            if [ $stat -eq 80 ]; then 
                aws ec2 start-instances --instance-ids $SERVERINSTANCEID
            fi
            echo "checking - status is ${stat}"
            stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
        done

        scp -i $SERVERSSHKEY $DATADIR/distrib/processed_trajectories.json ec2-user@$privip:data/distrib
        while [ $? -ne 0 ] ; do
            # in case the server isn't responding to ssh sessions yet
            sleep 10
            echo "server not responding yet, retrying"
            scp -i $SERVERSSHKEY $DATADIR/distrib/processed_trajectories.json ec2-user@$privip:data/distrib
        done 
        scp -i $SERVERSSHKEY $DATADIR/distrib/${rundate}*.json ec2-user@$privip:data/distrib
        
        echo "#!/bin/bash" > /tmp/execConsol.sh
        echo "export PYTHONPATH=/home/ec2-user/src/WesternMeteorPyLib:/home/ec2-user/src/ukmon_pylib" >> /tmp/execConsol.sh
        echo "python -m traj.consolidateDistTraj ~/data/distrib/ ~/data/distrib/processed_trajectories.json" >> /tmp/execConsol.sh
        chmod +x /tmp/execConsol.sh
        scp -i $SERVERSSHKEY /tmp/execConsol.sh ec2-user@$privip:data/distrib
        ssh -i $SERVERSSHKEY ec2-user@$privip "data/distrib/execConsol.sh"

        scp -i $SERVERSSHKEY ec2-user@$privip:data/distrib/processed_trajectories.json $DATADIR/distrib

        ssh -i $SERVERSSHKEY ec2-user@$privip "rm -f data/distrib/*.json"

        logger -s -t runDistrib "stopping calcserver again"
        aws ec2 stop-instances --instance-ids $SERVERINSTANCEID

        python -c "from traj.consolidateDistTraj import patchTrajDB ; patchTrajDB('$DATADIR/distrib/processed_trajectories.json','/home/ec2-user/ukmon-shared/matches/RMSCorrelate', '/home/ec2-user/data/distrib');"
    else
        python -m traj.consolidateDistTraj $DATADIR/distrib $DATADIR/distrib/processed_trajectories.json $rundate
    fi 
    # push the updated traj db to the S3 bucket
    aws s3 cp $DATADIR/distrib/processed_trajectories.json $UKMONSHAREDBUCKET/matches/distrib/ --quiet

    logger -s -t runDistrib "RUNTIME $SECONDS compressing the procssed data"
    gzip < $DATADIR/distrib/processed_trajectories.json > $DATADIR/trajdb/processed_trajectories.json.${rundate}.gz
    aws s3 mv $UKMONSHAREDBUCKET/matches/distrib/${rundate}.pickle $DATADIR/distrib --quiet
    tar czvf $DATADIR/distrib/${rundate}.tgz $DATADIR/distrib/${rundate}*.json $DATADIR/distrib/${rundate}.pickle
    aws s3 cp $DATADIR/distrib/${rundate}.tgz $UKMONSHAREDBUCKET/matches/distrib/done/ --quiet
    rm -f $DATADIR/distrib/${rundate}*.json $DATADIR/distrib/${rundate}.pickle
    aws s3 rm $UKMONSHAREDBUCKET/matches/distrib/ --exclude "*" --include "${rundate}*.json" --exclude "test/*" --recursive
else
    echo "trajectory database is size zero... not proceeding with copy"
fi 
# and then clear the profile again
unset AWS_PROFILE
logger -s -t runDistrib "RUNTIME $SECONDS finished runDistrib"
