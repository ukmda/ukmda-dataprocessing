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
source $here/../config.ini >/dev/null 2>&1
source $HOME/venvs/${WMPL_ENV}/bin/activate
$SRC/utils/clearCaches.sh

# get the date to operate for
if [ $# -eq 0 ]; then
    ym=$(date +%Y%m%d)
else
    ym=$1
fi

logger -s -t convertUfoToRms "starting"

python -m converters.UFOAtoFTPdetect $ym 30

$SRC/utils/clearCaches.sh
logger -s -t convertUfoToRms "finished"