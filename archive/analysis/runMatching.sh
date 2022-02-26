#
# start a big EC2 server to run the matching engine more quickly
# should process ~ 100 events in an hour on an 8-core server
#
# Parameters
#   none
#
# Consumes
#   All single-station data
#
# Produces
#   Solved trajectories
#
# NOTE: this script creates a script that executes on the target instance,
# not on the ukmonhelper instance


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
python -m traj.createExecMatchingSh $MATCHSTART $MATCHEND
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
