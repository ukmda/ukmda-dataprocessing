#
# Create density plots of meteor data
#
# Parameters:
#   date to process in yyyymm or yyyy format
#
# Consumes:
#   RMS format FTPdetect and platepars_all files for the date range chosen
#
# Produces:
#   A set of density plots in png format, and a text file summary
#     which are then synce to the website

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
source $HOME/venvs/${WMPL_ENV}/bin/activate

logger -s -t createDensityPlots "Create density and velocity plots by solar longitude for $ym"

if [ $ym == $yr ] ; then 
    python -m wmpl.Trajectory.AggregateAndPlot $MATCHDIR/RMSCorrelate/trajectories/$yr -p -s 30
    mkdir -p $MATCHDIR/RMSCorrelate/trajectories/$yr/plots > /dev/null 2>&1
    mv -f $MATCHDIR/RMSCorrelate/trajectories/$yr/*.png $MATCHDIR/RMSCorrelate/trajectories/$yr/plots
    mv -f $MATCHDIR/RMSCorrelate/trajectories/$yr/trajectory_summary.txt $MATCHDIR/RMSCorrelate/trajectories/$yr/plots
    aws s3 sync $MATCHDIR/RMSCorrelate/trajectories/$yr/plots $WEBSITEBUCKET/reports/$yr/orbits/plots --quiet
else
    python -m wmpl.Trajectory.AggregateAndPlot $MATCHDIR/RMSCorrelate/trajectories/$yr/$ym -p -s 30
    mkdir -p $MATCHDIR/RMSCorrelate/trajectories/$yr/$ym/plots > /dev/null 2>&1
    mv -f $MATCHDIR/RMSCorrelate/trajectories/$yr/$ym/*.png $MATCHDIR/RMSCorrelate/trajectories/$yr/$ym/plots
    mv -f $MATCHDIR/RMSCorrelate/trajectories/$yr/$ym/trajectory_summary.txt $MATCHDIR/RMSCorrelate/trajectories/$yr/$ym/plots
    aws s3 sync $MATCHDIR/RMSCorrelate/trajectories/$yr/$ym/plots $WEBSITEBUCKET/reports/$yr/orbits/$ym/plots --quiet
fi 