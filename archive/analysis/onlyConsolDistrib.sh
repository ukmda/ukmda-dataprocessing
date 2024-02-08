#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# just consolidate solutions of distributed candidates 
#
# Used if consolidating a bunch of candidates that were solved outside the normal process
#
# consumes: the trajdb and solution json files
# creates: an updated trajdb and hopefully additional orbits
#

"""
To use this function, first create the candidate pickle files, then copy them to the candidates
folder on the calcserver and submit them to the distributed processing engine with the following:

source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}
export PYTHONPATH=/home/ec2-user/src/WesternMeteorPyLib:/home/ec2-user/src/ukmon_pylib
export AWS_PROFILE=ukmonshared
cd /home/ec2-user/ukmon-shared/matches/RMSCorrelate/candidates
time python -m traj.distributeCandidates 20230113 /home/ec2-user/ukmon-shared/matches/RMSCorrelate/candidates $UKMONSHAREDBUCKET/matches/distrib

when this completes, logoff the calcserver and shut it down again
On the ukmonhelper run this script to wait for the distrib processing to finish and then 
merge in the data


"""


here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
logger -s -t onlyConsolDistrib "starting onlyConsolDistrib"

# load the configuration
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

# set the profile to the EE account so we can run the server and monitor progress
export AWS_PROFILE=ukmonshared


if [ "$1" == "" ] ; then 
    rundate=$(date --date="-$MATCHEND days" '+%Y%m%d')
else
    rundate=$1
fi 
logger -s -t onlyConsolDistrib "consolidating for $rundate"

python -c "from traj.distributeCandidates import monitorProgress as mp; mp('${rundate}'); "

privip=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].PublicIpAddress --output text --profile ukmonshared)
while [ "$privip" == "" ] ; do
    sleep 5
    echo "getting ipaddress"
    privip=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].PublicIpAddress --output text --profile ukmonshared)
done

if [ -s $DATADIR/distrib/processed_trajectories.json ] ; then 
    aws s3 sync $UKMONSHAREDBUCKET/matches/distrib/ $DATADIR/distrib/ --exclude "*" --include "*.json" --quiet
    cp -f $DATADIR/distrib/processed_trajectories.json $DATADIR/distrib/prev_processed_trajectories.json

    numtoconsol=$(ls -1 $DATADIR/distrib/${rundate}*.json | wc -l)
    if [ $numtoconsol -gt 5 ] ; then 
        logger -s -t onlyConsolDistrib "restarting calcserver to consolidate results"
        stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text --profile ukmonshared)
        if [ $stat -eq 80 ]; then 
            aws ec2 start-instances --instance-ids $SERVERINSTANCEID --profile ukmonshared
        fi
        logger -s -t onlyConsolDistrib "waiting for the server to be ready"
        while [ "$stat" -ne 16 ]; do
            sleep 30
            if [ $stat -eq 80 ]; then 
                aws ec2 start-instances --instance-ids $SERVERINSTANCEID --profile ukmonshared
            fi
            echo "checking - status is ${stat}"
            stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text --profile ukmonshared)
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
        echo "python -m traj.consolidateDistTraj ~/data/distrib/ ~/data/distrib/processed_trajectories.json ${rundate}" >> /tmp/execConsol.sh
        chmod +x /tmp/execConsol.sh
        scp -i $SERVERSSHKEY /tmp/execConsol.sh ec2-user@$privip:data/distrib
        ssh -i $SERVERSSHKEY ec2-user@$privip "data/distrib/execConsol.sh"

        scp -i $SERVERSSHKEY ec2-user@$privip:data/distrib/processed_trajectories.json $DATADIR/distrib

        ssh -i $SERVERSSHKEY ec2-user@$privip "rm -f data/distrib/*.json"

        logger -s -t runDistrib "stopping calcserver again"
        aws ec2 stop-instances --instance-ids $SERVERINSTANCEID --profile ukmonshared

        python -c "from traj.consolidateDistTraj import patchTrajDB ; patchTrajDB('$DATADIR/distrib/processed_trajectories.json','/home/ec2-user/ukmon-shared/matches/RMSCorrelate', '/home/ec2-user/data/distrib');"
    else
        python -m traj.consolidateDistTraj $DATADIR/distrib $DATADIR/distrib/processed_trajectories.json $rundate
    fi 
    # push the updated traj db to the S3 bucket
    aws s3 cp $DATADIR/distrib/processed_trajectories.json $UKMONSHAREDBUCKET/matches/distrib/ --quiet

    logger -s -t onlyConsolDistrib "compressing the procssed data"
    gzip < $DATADIR/distrib/processed_trajectories.json > $DATADIR/trajdb/processed_trajectories.json.${rundate}.gz
    aws s3 mv $UKMONSHAREDBUCKET/matches/distrib/${rundate}.pickle $DATADIR/distrib --quiet
    tar czvf $DATADIR/distrib/${rundate}.tgz $DATADIR/distrib/${rundate}*.json $DATADIR/distrib/${rundate}.pickle
    aws s3 cp $DATADIR/distrib/${rundate}.tgz $UKMONSHAREDBUCKET/matches/distrib/done/ --quiet
    rm -f $DATADIR/distrib/${rundate}*.json $DATADIR/distrib/${rundate}.pickle
    aws s3 rm $UKMONSHAREDBUCKET/matches/distrib/ --exclude "*" --include "${rundate}*.json" --exclude "test/*" --recursive
else
    echo "trajectory database is size zero... not proceeding with copy"
fi 
python -m reports.reportOfLatestMatches $DATADIR/distrib $DATADIR $MATCHEND $rundate processed_trajectories.json
dailyrep=$(ls -1tr $DATADIR/dailyreports/20* | tail -1)
$SRC/website/updateIndexPages.sh $dailyrep
logger -s -t onlyConsolDistrib "finished"
