#!/bin/bash
#
# Script to find correlated events, solve for their trajectories and orbits,
# then copy the results to the Archive website. 
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration and website keys
source $here/../config/config.ini >/dev/null 2>&1
source ~/.ssh/ukmon-shared-keys

# get the date to operate for
if [ $# -eq 0 ]; then
    ym=$(date +%Y%m)
else
    ym=$1
fi
yr=${ym:0:4}
mth=${ym:4:2}

# folder for logs
mkdir -p $SRC/logs/matches > /dev/null 2>&1

#python $here/consolidateMatchedData.py $yr $mth |tee $SRC/logs/matches/$ym.log
# get all UFO data into the right format
$SRC/analysis/convertUfoToRms.sh $ym
dom=`date '+%d'`
if [ $dom -lt 10 ] ; then 
    lastmth=`date --date='-1 month' '+%Y%m'`
    $SRC/analysis/convertUfoToRms.sh $lastmth
fi

# load the WMPL environment for the matching engine
cd $wmpl_loc
source ~/venvs/${WMPL_ENV}/bin/activate
export PYTHONPATH=$wmpl_loc:$PYLIB

# set the date range for the solver
startdt=$(date --date="-$MATCHSTART days" '+%Y%m%d-080000')
enddt=$(date --date="-$MATCHEND days" '+%Y%m%d-080000')

echo "solving for ${startdt} to ${enddt}"
python -m wmpl.Trajectory.CorrelateRMS $MATCHDIR/RMSCorrelate/ -l -r "($startdt,$enddt)"

# check if the solver had some sort of failiure - if the message is present it succeeded
logf=$(ls -1tr $SRC/logs/matches/matches*.log | tail -1)
success=$(grep "SOLVING RUN DONE" $logf)

if [ "$success" == "" ]
then
    export SRC
    python $PYLIB/utils/sendAnEmail.py markmcintyre99@googlemail.com "problem with matching" "Error"
    echo problems with solver
fi
echo "Solving run done"
echo "================"

# update the website 
# loop over new matches, creating an index page
cd $here/../website
find $MATCHDIR/RMSCorrelate/trajectories/ -type d -mtime -1 | while read i
do
    loc=$(basename $i)
    $SRC/website/createPageIndex.sh $i

    # copy the orbit file for consolidation and reporting
    cp $i/*orbit.csv ${RCODEDIR}/DATA/orbits/$yr/csv/
done
# backup the solved trajectory data
cp $MATCHDIR/RMSCorrelate/processed_trajectories.json $SRC/bkp/processed_trajectories.json.$(date +%Y%m%d)
gzip $SRC/bkp/processed_trajectories.json.$(date +%Y%m%d)

# update the Index page for the month and the year
$SRC/website/createOrbitIndex.sh ${yr}${mth}
$SRC/website/createOrbitIndex.sh ${yr}

# create text file containing most recent matches
cd $here
python $PYLIB/traj/reportOfLatestMatches.py $MATCHDIR/RMSCorrelate/trajectories

# purge old logs
find $SRC/logs/matches -name "matches*" -mtime +7 -exec rm -f {} \;