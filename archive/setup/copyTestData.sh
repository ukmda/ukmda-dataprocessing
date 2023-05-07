# prep some test data
$yr=$(date +%Y)

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1

rsync -avz ~/prod/data/single/*${yr}* $DATADIR/single/
rsync -avz ~/prod/data/matched/*${yr}* $DATADIR/matched/
rsync -avz ~/prod/data/consolidated/*${yr}* $DATADIR/consolidated/
rsync -avz ~/prod/data/consolidated/camera-details.csv $DATADIR/consolidated/
rsync -avz ~/prod/data/dailyreports/stats.txt $DATADIR/dailyreports/
rsync -avz ~/prod/data/dailyreports/${yr}*.txt $DATADIR/dailyreports/
rsync -avz ~/prod/logs/*${yr}*.txt $SRC/logs/
