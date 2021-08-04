#
# start a big EC2 server to run the matching engine more quickly
# should process ~ 100 events in an hour on an 8-core server
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration
source $here/../config/config.ini >/dev/null 2>&1

source $SERVERAWSKEYS
AWS_DEFAULT_REGION=eu-west-2 

logger -s -t runMatching "checking correlation server status and starting it"
stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
if [ $stat -eq 80 ]; then 
    aws ec2 start-instances --instance-ids $SERVERINSTANCEID
fi
logger -s -t runMatching "waiting for the server to be ready"
while [ "$stat" -ne 16 ]; do
    sleep 5
    echo "checking"
    stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
done
logger -s -t runMatching "ready to use"
sleep 20

# create the script to run the matching process
# could store this on the server permanently but this allows me to more readily
# make changes
logger -s -t runMatching "create the run script"
execMatchingsh=/tmp/execMatching.sh
thisip=$(curl --silent http://169.254.169.254/latest/meta-data/local-ipv4) 
startdt=$(date --date="-$MATCHSTART days" '+%Y%m%d-080000')
enddt=$(date --date="-$MATCHEND days" '+%Y%m%d-080000')

echo '#!/bin/bash' > $execMatchingsh
echo "source /home/ec2-user/venvs/wmpl/bin/activate" >> $execMatchingsh
echo "export PYTHONPATH=/home/ec2-user/src/WesternMeteorPyLib/" >> $execMatchingsh
echo "cd /home/ec2-user/data/RMSCorrelate" >> $execMatchingsh
echo "source $UKMONSHAREDKEY" >> $execMatchingsh
echo 'aws s3 sync s3://ukmon-shared/matches/RMSCorrelate/ . --exclude "*" --include "UK*" --quiet'  >> $execMatchingsh
#echo 'aws s3 cp s3://ukmon-shared/matches/RMSCorrelate/processed_trajectories.json.bigserver ./processed_trajectories.json' --quiet >> $execMatchingsh
echo "cd /home/ec2-user/src/WesternMeteorPyLib/" >> $execMatchingsh
echo "time python -m wmpl.Trajectory.CorrelateRMS /home/ec2-user/data/RMSCorrelate/ -l -r \"($startdt,$enddt)\"" >> $execMatchingsh
echo "source $UKMONSHAREDKEY" >> $execMatchingsh
echo "cd /home/ec2-user/data/RMSCorrelate" >> $execMatchingsh
echo "aws s3 sync trajectories/ s3://ukmon-shared/matches/RMSCorrelate/trajectories/ --quiet" >> $execMatchingsh
echo "aws s3 cp processed_trajectories.json s3://ukmon-shared/matches/RMSCorrelate/processed_trajectories.json.bigserver" >> $execMatchingsh
#echo "rsync -cavz trajectories/ $thisip:ukmon-shared/matches/RMSCorrelate/trajectories/" >> $execMatchingsh
#echo "scp processed_trajectories.json $thisip:ukmon-shared/matches/RMSCorrelate/processed_trajectories.json.bigserver" >> $execMatchingsh
chmod +x $execMatchingsh

logger -s -t runMatching "get server details"
privip=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].PrivateIpAddress --output text)

logger -s -t runMatching "deploy the script to the server and run it"

scp -i $SERVERSSHKEY $execMatchingsh ec2-user@$privip:/tmp
while [ $? -eq 255 ] ; do
    # in case the server isn't responding to ssh sessions yet
    scp -i $SERVERSSHKEY $execMatchingsh ec2-user@$privip:/tmp
done 
ssh -i $SERVERSSHKEY ec2-user@$privip $execMatchingsh

logger -s -t runMatching "job run, stop the server again"
aws ec2 stop-instances --instance-ids $SERVERINSTANCEID

logger -s -t runMatching "finished"
