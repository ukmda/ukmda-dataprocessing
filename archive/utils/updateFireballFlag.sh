#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
# mark a matched event as a fireball
#
# Parameters
#   orbitname eg 20220331_035554.395_UK
# 
# Consumes
#   matched csv and parquet files
#
# Produces
#   updated csv and parquet files
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration
source $here/../config.ini >/dev/null 2>&1

conda activate $HOME/miniconda3/envs/${WMPL_ENV}
export PYTHONPATH=$PYLIB

orbname="$1"
tof="$2"

if [[ "$orbname" == "" || "$tof" == "" ]] ; then 
    echo "usage: ./updateFireballFlag.sh orbname True/False"
    echo " eg ./updateFireballFlag.sh 20220331_035554.123_UK True"
    exit
fi

echo $orbname $tof
python << EOD
from reports.findFireballs import markAsFireball;
markAsFireball('${orbname}', ${tof});
EOD
yr=${orbname:0:4}
mdfile=reports/${yr}/fireballs/${orbname:0:15}.md
if [[ -f $DATADIR/$mdfile && "$tof" == "False" ]] ; then 
    rm -f $mdfile 
    aws s3 rm $WEBSITEBUCKET/$mdfile
fi
${SRC}/website/createFireballPage.sh ${yr} -3.99

aws s3 sync $DATADIR/matched/ $UKMONSHAREDBUCKET/matches/matched/ --quiet --include "*" --exclude "*.snap" --exclude "*.bkp" --exclude "*.gzip"
aws s3 sync $DATADIR/matched/ $UKMONSHAREDBUCKET/matches/matchedpq/ --quiet --exclude "*" --include "*.snap" --exclude "*.bkp" --exclude "*.gzip"
