#
# start a big EC2 server to run the matching engine more quickly
# should process ~ 100 events in an hour on an 8-core server
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration
source $here/../config/config.ini >/dev/null 2>&1

source ~/.ssh/marks-keys 
AWS_DEFAULT_REGION=eu-west-2 

stat=$(aws ec2 describe-instances --instance-ids i-08d709f5816f7de05 --query Reservations[*].Instances[*].State.Code --output text)
if [ $stat -eq 80 ]; then 
    aws ec2 start-instances --instance-ids i-08d709f5816f7de05
fi
echo "waiting for server to be ready"
while [ "$stat" -ne 16 ]; do
    sleep 5
    echo "checking"
    stat=$(aws ec2 describe-instances --instance-ids i-08d709f5816f7de05 --query Reservations[*].Instances[*].State.Code --output text)
done
echo "ready to use"
sleep 20

# create the script to run the matching process
# could store this on the server permanently but this allows me to more readily
# make changes
execMatchingsh=/tmp/execMatching.sh
thisip=$(curl --silent http://169.254.169.254/latest/meta-data/local-ipv4) 
startdt=$(date --date="-$MATCHSTART days" '+%Y%m%d-080000')
enddt=$(date --date="-$MATCHEND days" '+%Y%m%d-080000')

echo '#\!/bin/bash' > $execMatchingsh
echo "source /home/ec2-user/venvs/wmpl/bin/activate" >> $execMatchingsh
echo "export PYTHONPATH=/home/ec2-user/src/WesternMeteorPyLib/" >> $execMatchingsh
echo "cd /home/ec2-user/data/RMSCorrelate" >> $execMatchingsh
echo "source ~/.ssh/ukmon-shared-keys" >> $execMatchingsh
echo 'aws s3 sync s3://ukmon-shared/matches/RMSCorrelate/ . --exclude "*" --include "UK*"' >> $execMatchingsh
echo "cd /home/ec2-user/src/WesternMeteorPyLib/" >> $execMatchingsh
echo "time python -m wmpl.Trajectory.CorrelateRMS /home/ec2-user/data/RMSCorrelate/ -l -r \"($startdt,$enddt)\"" >> $execMatchingsh
echo "source ~/.ssh/ukmon-shared-keys" >> $execMatchingsh
echo "cd /home/ec2-user/data/RMSCorrelate" >> $execMatchingsh
echo "rsync -cavz trajectories/ $thisip:ukmon-shared/matches/RMSCorrelate/trajectories/" >> $execMatchingsh
echo "scp processed_trajectories.json $thisip:ukmon-shared/matches/RMSCorrelate/processed_trajectories.json.bigserver" >> $execMatchingsh
chmod +x $execMatchingsh

# get the private IP of the server
privip=$(aws ec2 describe-instances --instance-ids i-08d709f5816f7de05 --query Reservations[*].Instances[*].PrivateIpAddress --output text)

# copy the script and run it
scp -i ~/.ssh/markskey.pem $execMatchingsh ec2-user@$privip:/tmp
while [ $? -eq 255 ] ; do
    # in case the server isn't responding to ssh sessions yet
    scp -i ~/.ssh/markskey.pem $execMatchingsh ec2-user@$privip:/tmp
done 
ssh -i ~/.ssh/markskey.pem ec2-user@$privip $execMatchingsh

aws ec2 stop-instances --instance-ids i-08d709f5816f7de05
