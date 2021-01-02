#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source ~/.ssh/ukmon-shared-keys
source ~/venvs/wmpl/bin/activate
source ~/src/analysis/config.ini

if [ $# -eq 0 ]; then
    ym=202001
else
    ym=$1
fi
yr=${ym:0:4}
mth=${ym:4:2}

mkdir -p $here/logs > /dev/null 2>&1

python $here/consolidateMatchedData.py $yr $mth |tee $here/logs/$ym.log
