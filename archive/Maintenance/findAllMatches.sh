#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source ~/.ssh/ukmon-shared-keys
source ~/venvs/${WMPL_ENV}/bin/activate

if [[ "$here" == *"prod"* ]] ; then
    echo sourcing prod config
    source $HOME/prod/config/config.ini >/dev/null 2>&1
else
    echo sourcing dev config
    source $HOME/src/config/config.ini >/dev/null 2>&1
fi

if [ $# -eq 0 ]; then
    ym=$(date +%Y%m)
else
    ym=$1
fi
yr=${ym:0:4}
mth=${ym:4:2}

mkdir -p $here/logs > /dev/null 2>&1

python $here/consolidateMatchedData.py $yr $mth |tee $here/logs/$ym.log
