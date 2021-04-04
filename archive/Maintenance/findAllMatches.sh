#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1

source ~/.ssh/ukmon-shared-keys
source ~/venvs/${WMPL_ENV}/bin/activate

if [ $# -eq 0 ]; then
    ym=$(date +%Y%m)
else
    ym=$1
fi
yr=${ym:0:4}
mth=${ym:4:2}

mkdir -p $SRC/logs/matches > /dev/null 2>&1

#python $here/consolidateMatchedData.py $yr $mth |tee $SRC/logs/matches/$ym.log


# run the matching engine
cd $wmpl_loc
source ~/venvs/${WMPL_ENV}/bin/activate
export PYTHONPATH=$wmpl_loc

startdt=$(date --date='-14 days' '+%Y%m%d-000001')
enddt=$(date '+%Y%m%d-%H%m%S')
python -m wmpl.Trajectory.CorrelateRMS $MATCHDIR/RMSCorrelate/ -l -r "($startdt,$enddt)" |tee $SRC/logs/matches/$ym.log

# create text file containing most recent matches
cd $here
python reportOfLatestMatches.py $MATCHDIR/RMSCorrelate/trajectories

# update the website 
cd $here/../website
find $MATCHDIR/RMSCorrelate/trajectories/ -type d -mtime -1 | while read i
do
    loc=$(basename $i)
    ./createPageIndex.sh $i
    # copy the orbit file for consoltion
    # and reporting
    cp $i/*orbit.csv ${RCODEDIR}/DATA/orbits/$yr/csv/
done
./createOrbitIndex.sh ${yr}${mth}
./createOrbitIndex.sh ${yr}
