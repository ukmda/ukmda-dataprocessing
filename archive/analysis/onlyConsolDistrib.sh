#!/bin/bash
#
# just consolidate solutions of distributed candidates 
#
# Used if consolidating a bunch of json trajdbs that were solved outside the normal process
#
# consumes: the trajdb and solution json files
# creates: an updated trajdb and hopefully additional orbits
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
logger -s -t runDistrib "RUNTIME $SECONDS starting runDistrib"

# load the configuration
source $here/../config.ini >/dev/null 2>&1

# set the profile to the EE account so we can run the server and monitor progress
export AWS_PROFILE=ukmonshared

begdate=$(date --date="-$MATCHSTART days" '+%Y%m%d')
rundate=$(date --date="-$MATCHEND days" '+%Y%m%d')

privip=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].PrivateIpAddress --output text)
while [ "$privip" == "" ] ; do
    sleep 5
    echo "getting ipaddress"
    privip=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].PrivateIpAddress --output text)
done

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
python -m reports.reportOfLatestMatches $DATADIR/distrib $DATADIR $MATCHEND $rundate processed_trajectories.json
dailyrep=$(ls -1tr $DATADIR/dailyreports/20* | tail -1)
$SRC/website/updateIndexPages.sh $dailyrep

