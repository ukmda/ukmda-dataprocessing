#!/bin/bash
#
# Script to find correlated events, solve for their trajectories and orbits,
# then copy the results to the Archive website. 
# Parameters:
#   optional start and end days back to process. 
#   If not supplied, the environment variables MATCHSTART and MATCHEND are used
#
# Consumes:
#   All UFO and RMS single-station data (ftpdetect, platepars_all and A.xml files)
#
# Produces:
#   new and updated orbit solutions in $MATCHDIR/RMSCorrelate/trajectories 
#   csv and extracsv files in $DATADIR/orbits/yyyy/csv and extracsv
#   daily report of matches and statistics, in $DATADIR/dailyreports
#   an email sent out via a lambda fn
#   updated orbit page, monthly and annual indexes for the website


here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration and website keys
source $here/../config/config.ini >/dev/null 2>&1
source $UKMONSHAREDKEY

# read start/end dates from commandline if rerunning for historical date
if [ $# -gt 0 ] ; then
    if [ "$1" != "" ] ; then
        echo "selecting range"
        MATCHSTART=$1
    fi
    if [ "$2" != "" ] ; then
        MATCHEND=$(( $MATCHSTART - $2 ))
    else
        echo "matchend was not supplied, using 2"
        MATCHEND=$(( $MATCHSTART - 2 ))
    fi
fi


# folder for logs
mkdir -p $SRC/logs > /dev/null 2>&1

logger -s -t findAllMatches "load the WMPL environment and set PYTHONPATH for the matching engine"

source ~/venvs/${WMPL_ENV}/bin/activate
export PYTHONPATH=$wmpl_loc:$PYLIB

logger -s -t findAllMatches "get all UFO data into the right format"
$SRC/analysis/convertUfoToRms.sh
dom=`date '+%d'`
if [ $dom -lt 10 ] ; then 
    lastmth=`date --date='-1 month' '+%Y%m'`
    $SRC/analysis/convertUfoToRms.sh $lastmth
fi
logger -s -t findAllMatches "create ukmon specific merged single-station data file"
$SRC/analysis/getRMSSingleData.sh

logger -s -t findAllMatches "set the date range for the solver"
cd $wmpl_loc

startdt=$(date --date="-$MATCHSTART days" '+%Y%m%d-080000')
enddt=$(date --date="-$MATCHEND days" '+%Y%m%d-080000')
logger -s -t findAllMatches "solving for ${startdt} to ${enddt}"

thisjson=$MATCHDIR/RMSCorrelate/processed_trajectories.json.bigserver
cp $thisjson $MATCHDIR/RMSCorrelate/prev_processed_trajectories.json.bigserver

$SRC/analysis/runMatching.sh

logger -s -t findAllMatches "check if the solver had some sort of failiure"
logf=$(ls -1tr $SRC/logs/matches-*.log | tail -1)
success=$(grep "SOLVING RUN DONE" $logf)

if [ "$success" == "" ]
then
    export SRC
    python $PYLIB/utils/sendAnEmail.py markmcintyre99@googlemail.com "problem with matching" "Error"
    echo problems with solver
fi
logger -s -t findAllMatches "Solving run done"
logger -s -t findAllMatches "================"

cd $here
logger -s -t findAllMatches "create text file containing most recent matches"
python $PYLIB/reports/reportOfLatestMatches.py $MATCHDIR/RMSCorrelate $DATADIR $MATCHEND

logger -s -t findAllMatches "update the website loop over new matches creating an index page and copying files"
dailyrep=$(ls -1tr $DATADIR/dailyreports/20* | tail -1)
trajlist=$(cat $dailyrep | awk -F, '{print $2}')

# create extra datafiles
export DATADIR # used by extraDatafiles
python $PYLIB/traj/extraDataFiles.py $dailyrep

# now create page indexes and update website
cd $here/../website
yr=$(date +%Y)
for traj in $trajlist 
do
    $SRC/website/createPageIndex.sh $traj

    # copy the orbit file for consolidation and reporting
    cp $traj/*orbit.csv ${DATADIR}/orbits/$yr/csv/
    cp $traj/*orbit_extras.csv ${DATADIR}/orbits/$yr/extracsv/
done

logger -s -t findAllMatches "gather some stats"
matchlog=$( ls -1 ${SRC}/logs/matches-*.log | tail -1)
vals=$(python $SRC/ukmon_pylib/utils/getMatchStats.py $matchlog )
evts=$(echo $vals | awk '{print $2}')
trajs=$(echo $vals | awk '{print $6}')
matches=$(wc -l $dailyrep | awk '{print $1}')
rtim=$(grep "Total run time" $matchlog | awk '{print $4}')
echo $(basename $dailyrep) $evts $trajs $matches $rtim >>  $DATADIR/dailyreports/stats.txt

if [ "$RUNTIME_ENV" == "PROD" ] ; then 
    # copy back so the daily report can run
    rsync -avz $DATADIR/dailyreports/ $MATCHDIR/RMSCorrelate/dailyreports/
fi 

logger -s -t findAllMatches "backup the solved trajectory data"

lastjson=$(ls -1tr $SRC/bkp/| grep -v ".gz" | tail -1)
thisjson=$MATCHDIR/RMSCorrelate/processed_trajectories.json.bigserver
cp $thisjson $SRC/bkp/processed_trajectories.json.$(date +%Y%m%d).bigserver
gzip $SRC/bkp/$lastjson

logger -s -t findAllMatches "update the Index page for the month and the year"

for traj in $trajlist ; do bn=$(basename $traj); echo ${bn:0:8} >> /tmp/days.txt ; done
daystodo=$(cat /tmp/days.txt | sort | uniq)
for dtd in $daystodo
do
    $SRC/website/createOrbitIndex.sh ${dtd}
done
rm /tmp/days.txt

for traj in $trajlist ; do bn=$(basename $traj); echo ${bn:0:6} >> /tmp/days.txt ; done
daystodo=$(cat /tmp/days.txt | sort | uniq)
for dtd in $daystodo
do
    $SRC/website/createOrbitIndex.sh ${dtd}
done
rm /tmp/days.txt

for traj in $trajlist ; do bn=$(basename $traj); echo ${bn:0:4} >> /tmp/days.txt ; done
daystodo=$(cat /tmp/days.txt | sort | uniq)
for ytd in $daystodo
do
    $SRC/website/createOrbitIndex.sh ${ytd}
done
rm /tmp/days.txt

logger -s -t findAllMatches "purge old logs"
find $SRC/logs -name "matches*" -mtime +7 -exec gzip {} \;
find $SRC/logs -name "matches*" -mtime +30 -exec rm -f {} \;

logger -s -t findAllMatches "Matching process finished"