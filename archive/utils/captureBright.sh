#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

cd $DATADIR/brightness
rundt=$(date -d "yesterday" +%Y%m%d)
python -m analysis.compareBrightnessData $rundt

$here/updateDb.sh $rundt

