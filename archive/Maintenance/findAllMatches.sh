#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1

source ~/.ssh/ukmon-shared-keys
source ~/venvs/${WMPL_ENV}/bin/activate

if [ $# -eq 0 ]; then
    ym=$(date +%Y%m)
else
    ym=$1
fi
yr=${ym:0:4}
mth=${ym:4:2}

mkdir -p $SRC/logs/matches > /dev/null 2>&1

python $here/consolidateMatchedData.py $yr $mth |tee $SRC/logs/matches/$ym.log

cd $wmpl_loc
source ~/venvs/${WMPL_ENV}/bin/activate
python -m wmpl.Trajectory.CorrelateRMS ~/ukmon-shared/matches/RMSCorrelate/ -l