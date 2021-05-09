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

logger -s -t findAllMatches "load the WMPL environment and set PYTHONPATH for the matching engine"

source ~/venvs/${WMPL_ENV}/bin/activate
export PYTHONPATH=$wmpl_loc:$PYLIB

logger -s -t findAllMatches "get all UFO data into the right format"
$SRC/analysis/convertUfoToRms.sh $ym
dom=`date '+%d'`
if [ $dom -lt 10 ] ; then 
    lastmth=`date --date='-1 month' '+%Y%m'`
    $SRC/analysis/convertUfoToRms.sh $lastmth
fi

logger -s -t findAllMatches "set the date range for the solver"
cd $wmpl_loc

startdt=$(date --date="-$MATCHSTART days" '+%Y%m%d-080000')
enddt=$(date --date="-$MATCHEND days" '+%Y%m%d-080000')
logger -s -t findAllMatches "solving for ${startdt} to ${enddt}"

$SRC/analysis/runMatching.sh

#python -m wmpl.Trajectory.CorrelateRMS $MATCHDIR/RMSCorrelate/ -l -r "($startdt,$enddt)"

logger -s -t findAllMatches "check if the solver had some sort of failiure"
logf=$(ls -1tr $SRC/logs/matches/matches*.log | tail -1)
success=$(grep "SOLVING RUN DONE" $logf)

if [ "$success" == "" ]
then
    export SRC
    python $PYLIB/utils/sendAnEmail.py markmcintyre99@googlemail.com "problem with matching" "Error"
    echo problems with solver
fi
logger -s -t findAllMatches "Solving run done"
logger -s -t findAllMatches "================"

logger -s -t findAllMatches "update the website loop over new matches, creating an index page and copying files"

cd $here
logger -s -t findAllMatches "create text file containing most recent matches"
python $PYLIB/traj/reportOfLatestMatches.py $MATCHDIR/RMSCorrelate/trajectories

dailyrep=$(ls -1tr $MATCHDIR/RMSCorrelate/dailyreports | tail -1)
trajlist=$(cat $MATCHDIR/RMSCorrelate/dailyreports/$dailyrep | awk -F, '{print $2}')

cd $here/../website
for traj in $trajlist 
do
    $SRC/website/createPageIndex.sh $MATCHDIR/RMSCorrelate/trajectories/$traj

    # copy the orbit file for consolidation and reporting
    cp $MATCHDIR/RMSCorrelate/trajectories/$traj/*orbit.csv ${DATADIR}/orbits/$yr/csv/
done

logger -s -t findAllMatches "Create density and velocity plots by solar longitude"
export PYTHONPATH=$wmpl_loc
python -m wmpl.Trajectory.AggregateAndPlot $MATCHDIR/RMSCorrelate/
mv -f $MATCHDIR/RMSCorrelate/*.png $MATCHDIR/RMSCorrelate/plots
source $WEBSITEKEY
aws s3 sync $MATCHDIR/RMSCorrelate/plots $WEBSITEBUCKET/reports/plots


logger -s -t findAllMatches "backup the solved trajectory data"

lastjson=$(ls -1tr $SRC/bkp/| grep -v ".gz" | tail -1)
#thisjson=$MATCHDIR/RMSCorrelate/processed_trajectories.json
#cp $thisjson $SRC/bkp/processed_trajectories.json.$(date +%Y%m%d)
thisjson=$MATCHDIR/RMSCorrelate/processed_trajectories.json.bigserver
cp $thisjson $SRC/bkp/processed_trajectories.json.$(date +%Y%m%d).bigserver
gzip $SRC/bkp/$lastjson

logger -s -t findAllMatches "update the Index page for the month and the year"

$SRC/website/createOrbitIndex.sh ${yr}${mth}
$SRC/website/createOrbitIndex.sh ${yr}

logger -s -t findAllMatches "purge old logs"
find $SRC/logs/matches -name "matches*" -mtime +7 -exec rm -f {} \;

logger -s -t findAllMatches "Matching process finished"