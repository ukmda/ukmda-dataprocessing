#
# python to create density plots of meteor data
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

if [ "$1" == "" ] ; then
    ym=$(date +%Y%m)
    yr=$(date +%Y)
else
    ym=$1
    yr=${ym:0:4}
fi

# load the configuration and website keys
source $here/../config/config.ini >/dev/null 2>&1

logger -s -t createDensityPlots "Create density and velocity plots by solar longitude for $ym"
export PYTHONPATH=$wmpl_loc

python -m wmpl.Trajectory.AggregateAndPlot $MATCHDIR/RMSCorrelate/trajectories/$yr/$ym -p
mkdir -p $MATCHDIR/RMSCorrelate/trajectories/$yr/$ym/plots > /dev/null 2>&1
mv -f $MATCHDIR/RMSCorrelate/trajectories/$yr/$ym/*.png $MATCHDIR/RMSCorrelate/trajectories/$yr/$ym/plots
mv -f $MATCHDIR/RMSCorrelate/trajectories/$yr/$ym/trajectory_summary.txt $MATCHDIR/RMSCorrelate/trajectories/$yr/$ym/plots
source $WEBSITEKEY
aws s3 sync $MATCHDIR/RMSCorrelate/trajectories/$yr/$ym/plots $WEBSITEBUCKET/reports/$yr/orbits/$ym/plots --quiet
