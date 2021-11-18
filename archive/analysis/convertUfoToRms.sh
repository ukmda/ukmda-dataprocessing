#
# Convert a month's worth of UFO data to RMS format
#
# Parameters:
#   month to process in yyyymm format
#
# Consumes:
#   UFO format data A.xml files
#
# Produces:
#   RMS format FTPdetect and platepars_all files, one per day

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration
source $here/../config/config.ini >/dev/null 2>&1
source ~/venvs/${WMPL_ENV}/bin/activate
export PYTHONPATH=$PYLIB:$wmpl_loc
export ARCHDIR

# get the date to operate for
if [ $# -eq 0 ]; then
    ym=$(date +%Y%m)
else
    ym=$1
fi
yr=${ym:0:4}

logger -s -t convertUfoToRms "starting"

python $PYLIB/converters/UFOAtoFTPdetect.py $ym $MATCHDIR/RMSCorrelate/

logger -s -t convertUfoToRms "finished"