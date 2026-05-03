#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

cd $DATADIR/brightness
rundt=$(date -d "yesterday" +%Y%m%d)
python -m utils.compareBrightnessData $rundt

$SRC/utils/loadBrightnessCsvMDB.sh

find ${DATADIR}/brightness -name "CaptureNight*" -mtime +30 -exec rm -f {} \;
find ${DATADIR}/brightness -name "matcheddata*" -mtime +30 -exec rm -f {} \;