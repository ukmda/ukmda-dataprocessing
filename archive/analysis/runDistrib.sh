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
source $here/../config/config.ini >/dev/null 2>&1

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
begdate=$(date --date="-$MATCHSTART days" '+%Y%m%d')
rundate=$(date --date="-$MATCHEND days" '+%Y%m%d')

logger -s -t runDistrib "running phase 1 for dates ${begdate} to ${rundate}"
source ~/venvs/${WMPL_ENV}/bin/activate
source $SERVERAWSKEYS
srcdir=$DATADIR/cameradata


logger -s -t runDistrib "synchronising the raw data"
time aws s3 sync ${UKMONSHAREDBUCKET}/matches/RMSCorrelate/ ${srcdir} --exclude "*" --include "UK*" --quiet

logger -s -t runDistrib "copying trajectory database"
time  python -c "from traj.consolidateDistTraj import patchTrajDB as pdb ; pdb('$MATCHDIR/RMSCorrelate/prev_processed_trajectories.json.bigserver','$srcdir');"

logger -s -t runDistrib "running correlator"
time python -m wmpl.Trajectory.CorrelateRMS $srcdir/ -l -r "(${begdate}-080000,${rundate}-080000)" -i 1

logger -s -t runDistrib "distributing the candidates"
time python -m traj.distributeCandidates ${rundate} $srcdir/candidates $MATCHDIR/distrib

logger -s -t runDistrib "merging in the new json files"
cp $srcdir/processed_trajectories.json $srcdir/processed_trajectories.json.bkp
python -m traj.consolidateDistTraj $MATCHDIR/distrib $srcdir/processed_trajectories.json

logger -s -t runDistrib "compressing the processed data"
if [ ! -d $srcdir/done ] ; then mkdir $srcdir/done ; fi
tar czvf $srcdir/done/${rundate}.tgz $srcdir/candidates/* $MATCHDIR/distrib/*.json
rm -f $srcdir/candidates/*
rm -f $MATCHDIR/distrib/*.json
mv $MATCHDIR/distrib/${rundate}.pickle $srcdir/done
logger -s -t runDistrib "done"

