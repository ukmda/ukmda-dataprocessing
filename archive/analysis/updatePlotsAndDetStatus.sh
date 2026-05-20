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

logger -s -t $(basename $0 .sh) "starting"

if [ $# -gt 0 ] ; then
    if [ "$1" != "" ] ; then
        MATCHSTART=$1
    fi
    if [ "$2" != "" ] ; then
        MATCHEND=$2
    else
        MATCHEND=$(( $MATCHSTART - 2 ))
    fi
fi
begdate=$(date --date="-$MATCHSTART days" '+%Y%m%d')
rundate=$(date --date="-$MATCHEND days" '+%Y%m%d')

logger -s -t $(basename $0 .sh) "updating plots etc for dates ${begdate} to ${rundate}"
logger -s -t $(basename $0 .sh) "start correlation server"

stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
if [ $stat -eq 80 ]; then 
    aws ec2 start-instances --instance-ids $SERVERINSTANCEID
fi
while [ "$stat" -ne 16 ]; do
    sleep 5
    stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
done

conda activate $HOME/miniconda3/envs/${WMPL_ENV}

logger -s -t $(basename $0 .sh) "creating the run script"
execrerun=execreplot.sh
execrerunsh=/tmp/$execrerun
python -c "from traj.createDistribMatchingSh import createExecReplotSh;createExecReplotSh($MATCHSTART, $MATCHEND, '$execrerunsh', '$TESTMODE')"
chmod +x $execrerunsh

logger -s -t updatePlotsAndDetStatus "deploy the script to the server $CALCSERVERIP and run it"

scp -i $SERVERSSHKEY $execrerunsh $SERVERUSERID@$CALCSERVERIP:runtime/scripts/$execrerun
while [ $? -ne 0 ] ; do
    # in case the server isn't responding to ssh sessions yet
    sleep 10
    scp -i $SERVERSSHKEY $execrerunsh $SERVERUSERID@$CALCSERVERIP:runtime/scripts/$execrerun
done 
# push the python and templates required
rsync -avz  -e "ssh -i $SERVERSSHKEY" $PYLIB/traj/pickleAnalyser.py $SERVERUSERID@$CALCSERVERIP:src/ukmon_pylib/traj

# now run the script
ssh -i $SERVERSSHKEY $SERVERUSERID@$CALCSERVERIP "runtime/scripts/$execrerun"

logger -s -t $(basename $0 .sh) "job run, stop the server again"

aws ec2 stop-instances --instance-ids $SERVERINSTANCEID

logger -s -t $(basename $0 .sh) "get a list of uncalibrated data"

aws s3 sync $UKMONSHAREDBUCKET/matches/consumed/ $DATADIR/single/used/ --exclude "*" --include "*.txt" --quiet
rundate=$(cat $DATADIR/rundate.txt)
python -c "from utils.getUsedUnused import getUncalibratedImageList;getUncalibratedImageList('$rundate');"

# refresh the website index pages just in case any new data
dailyrep=$(ls -1tr $DATADIR/dailyreports/20* | tail -1)
$SRC/website/updateIndexPages.sh $dailyrep

logger -s -t $(basename $0 .sh) "finished"
