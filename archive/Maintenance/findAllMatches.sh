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


# load the WMPL environment for the matching engine
cd $wmpl_loc
source ~/venvs/${WMPL_ENV}/bin/activate
export PYTHONPATH=$wmpl_loc

# set the date range for the solver
startdt=$(date --date='-2 days' '+%Y%m%d-080000')
enddt=$(date '+%Y%m%d-080000')

echo "solving for ${startdt} to ${enddt}"
python -m wmpl.Trajectory.CorrelateRMS $MATCHDIR/RMSCorrelate/ -l -r "($startdt,$enddt)"

# check if the solver had some sort of failiure - if the message is present it succeeded
logf=$(ls -1tr $SRC/logs/matches/matches*.log | tail -1)
success=$(grep "SOLVING RUN DONE" $logf)

if [ "$success" == "" ]
then

    # email me an alert
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
    ./createPageIndex.sh $i

    # copy the orbit file for consolidation and reporting
    cp $i/*orbit.csv ${RCODEDIR}/DATA/orbits/$yr/csv/
done

# update the Index page for the month and the year
./createOrbitIndex.sh ${yr}${mth}
./createOrbitIndex.sh ${yr}

# create text file containing most recent matches
cd $here
python reportOfLatestMatches.py $MATCHDIR/RMSCorrelate/trajectories
