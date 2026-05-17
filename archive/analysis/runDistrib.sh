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

logger -s -t runDistrib "starting runDistrib" 

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

logger -s -t runDistrib "running phase 1 for dates ${begdate} to ${rundate}"

logger -s -t runDistrib  "start correlation server" 
aws ec2 start-instances --instance-ids $SERVERINSTANCEID
stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
while [ "$stat" -ne 16 ]; do
    sleep 5
    stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
done

conda activate $HOME/miniconda3/envs/${WMPL_ENV}

logger -s -t runDistrib "creating the run script"

execdist=execdistrib.sh
execMatchingsh=/tmp/$execdist
python -m traj.createDistribMatchingSh $MATCHSTART $MATCHEND $execMatchingsh $TESTMODE
chmod +x $execMatchingsh

logger -s -t runDistrib "deploy the script to the server $CALCSERVERIP and run it"

scp -i $SERVERSSHKEY $execMatchingsh $SERVERUSERID@$CALCSERVERIP:data/distrib/$execdist
while [ $? -ne 0 ] ; do
    # in case the server isn't responding to ssh sessions yet
    sleep 10
    scp -i $SERVERSSHKEY $execMatchingsh $SERVERUSERID@$CALCSERVERIP:data/distrib/$execdist
done 
# push the python code and ECS templates required
rsync -avz -e "ssh -i $SERVERSSHKEY" $PYLIB/traj/clusdetails-* $SERVERUSERID@$CALCSERVERIP:src/ukmon_pylib/traj/
rsync -avz -e "ssh -i $SERVERSSHKEY" $PYLIB/traj/taskrunner*.json $SERVERUSERID@$CALCSERVERIP:src/ukmon_pylib/traj/
rsync -avz -e "ssh -i $SERVERSSHKEY" $PYLIB/traj/consolidateDistTraj.py $SERVERUSERID@$CALCSERVERIP:src/ukmon_pylib/traj/
rsync -avz -e "ssh -i $SERVERSSHKEY" $PYLIB/traj/distributeCandidates.py $SERVERUSERID@$CALCSERVERIP:src/ukmon_pylib/traj/
rsync -avz -e "ssh -i $SERVERSSHKEY" $PYLIB/traj/pickleAnalyser.py $SERVERUSERID@$CALCSERVERIP:src/ukmon_pylib/traj/
rsync -avz -e "ssh -i $SERVERSSHKEY" $PYLIB/traj/ShowerAssociation.py $SERVERUSERID@$CALCSERVERIP:src/ukmon_pylib/traj/
rsync -avz -e "ssh -i $SERVERSSHKEY" $PYLIB/utils/convertSolLon.py $SERVERUSERID@$CALCSERVERIP:src/ukmon_pylib/utils/
rsync -avz -e "ssh -i $SERVERSSHKEY" $PYLIB/maintenance/dataMaintenance.py $SERVERUSERID@$CALCSERVERIP:src/ukmon_pylib/maintenance/

# now run the script
logger -s -t runDistrib "start distributed processing"
ssh -i $SERVERSSHKEY $SERVERUSERID@$CALCSERVERIP "data/distrib/$execdist"

rsync -avz -e "ssh -i $SERVERSSHKEY" $SERVERUSERID@$CALCSERVERIP:ukmon-shared/matches/RMSCorrelate/candidates/processed/*.tgz $DATADIR/distrib/candidates

rsync -avz -e "ssh -i $SERVERSSHKEY" $SERVERUSERID@$CALCSERVERIP:ukmon-shared/matches/RMSCorrelate/logs/*${rundate}*.log $SRC/logs/distrib/
ssh -i $SERVERSSHKEY $SERVERUSERID@$CALCSERVERIP "find ukmon-shared/matches/RMSCorrelate/logs -name '*.log' -mtime +30 -exec rm -f {} \;"

logger -s -t runDistrib "job run, stop the server again"
aws ec2 stop-instances --instance-ids $SERVERINSTANCEID

logger -s -t runDistrib "monitoring and waiting for completion"

python -c "from traj.distributeCandidates import monitorProgress as mp; mp('${rundate}', '${TESTMODE}'); "

mkdir -p $DATADIR/distrib
cd $DATADIR/distrib

logger -s -t runDistrib "restarting server to consolidate results"

stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
if [ $stat -eq 80 ]; then 
    aws ec2 start-instances --instance-ids $SERVERINSTANCEID
fi
while [ "$stat" -ne 16 ]; do
    sleep 30
    if [ $stat -eq 80 ]; then 
        aws ec2 start-instances --instance-ids $SERVERINSTANCEID
    fi
    stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
done

execcons=execconsol.sh
execConsolsh=/tmp/$execcons
python -c "from traj.createDistribMatchingSh import createExecConsolSh;createExecConsolSh($MATCHSTART, $MATCHEND, '$execConsolsh', '$TESTMODE')"
chmod +x $execConsolsh

logger -s -t runDistrib "running consolidation"

scp -i $SERVERSSHKEY $execConsolsh $SERVERUSERID@$CALCSERVERIP:data/distrib/$execcons
ssh -i $SERVERSSHKEY $SERVERUSERID@$CALCSERVERIP "data/distrib/$execcons"

logger -s -t runDistrib "finished consolidation, copying databases"

rsync -avz -e "ssh -i $SERVERSSHKEY" $SERVERUSERID@$CALCSERVERIP:ukmon-shared/matches/RMSCorrelate/dbs/*.db $DATADIR/distrib
ssh -i $SERVERSSHKEY $SERVERUSERID@$CALCSERVERIP "find /tmp -maxdepth 1 -name "*.pickle"  -mtime +7 -exec rm -f {} \;"

logger -s -t runDistrib "stopping calcserver again"
aws ec2 stop-instances --instance-ids $SERVERINSTANCEID

logger -s -t runDistrib "copying data to batch server and tidying up"

# grab a copy of the indvidual container dbs so we can get a list of new solutions
rm -Rf $DATADIR/latest/contdbs/
mkdir -p $DATADIR/latest/contdbs/
aws s3 sync $UKMONSHAREDBUCKET/matches/distrib${TESTSUFF}/ $DATADIR/latest/contdbs/ --exclude "*" --include "*.db" --exclude "dbs/*" --exclude "test/*" --quiet
aws s3 rm $UKMONSHAREDBUCKET/matches/distrib${TESTSUFF}/ --exclude "*" --include "*${rundate}*.db" --exclude "test/*" --exclude "dbs/*" --recursive --quiet
aws s3 mv $UKMONSHAREDBUCKET/matches/distrib${TESTSUFF}/${rundate}.pickle $DATADIR/distrib --quiet

# grab a copy of the indvidual container logs - duplicated in monitorProgress, but never mind
aws s3 sync $UKMONSHAREDBUCKET/matches/distrib${TESTSUFF}/ $SRC/logs/distrib/ --exclude "*" --include "correl*.log"  --exclude "logs/" --quiet
aws s3 rm $UKMONSHAREDBUCKET/matches/distrib${TESTSUFF}/ --exclude "*" --include "correl*.log"  --exclude "logs/" --recursive  --quiet

mkdir -p $DATADIR/trajdb
tar czvf $DATADIR/trajdb/databases_${rundate}.tgz $DATADIR/distrib/*.db
mkdir -p $DATADIR/distrib/containers
tar czvf $DATADIR/distrib/containers/contdbs_${rundate}.tgz $DATADIR/latest/contdbs/*.db $DATADIR/distrib/${rundate}.pickle
aws s3 cp $DATADIR/distrib/containers/contdbs_${rundate}.tgz $UKMONSHAREDBUCKET/matches/distrib${TESTSUFF}/done/ --quiet

tar czvf $DATADIR/distrib/containers/contlogs_${rundate}.tgz $SRC/logs/distrib/correlator_${rundate}*.log $SRC/logs/distrib/${rundate}_*.log

find $DATADIR/distrib/containers/ -name "cont*.tgz" -mtime +30 -exec rm -f {} \;
find $DATADIR/distrib/ -maxdepth 1 -name "20*.tgz" -mtime +30 -exec rm -f {} \;
rm -f $DATADIR/distrib/${rundate}.pickle

logger -s -t "finished runDistrib"
