#
# python to create density plots of meteor data
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration and website keys
source $here/../config/config.ini >/dev/null 2>&1

logger -s -t createDensityPlots "Create density and velocity plots by solar longitude"
export PYTHONPATH=$wmpl_loc
python -m wmpl.Trajectory.AggregateAndPlot $MATCHDIR/RMSCorrelate/ -p
mv -f $MATCHDIR/RMSCorrelate/*.png $MATCHDIR/RMSCorrelate/plots
source $WEBSITEKEY
aws s3 sync $MATCHDIR/RMSCorrelate/plots $WEBSITEBUCKET/reports/plots --quiet
