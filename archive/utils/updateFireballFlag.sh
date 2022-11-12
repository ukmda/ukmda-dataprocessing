#!/bin/bash
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

source ~/venvs/$WMPL_ENV/bin/activate
export PYTHONPATH=$PYLIB

orbname="$1"
tof="$2"
if [ "$tof" == "" ] ; then 
    tof="True"
fi

echo $orbname $tof
python << EOD
from reports.findFireballs import markAsFireball;
markAsFireball('${orbname}', ${tof});
EOD

aws s3 sync $DATADIR/matched/ $UKMONSHAREDBUCKET/matches/matched/ --quiet --include "*" --exclude "*.snap" --exclude "*.bkp" --exclude "*.gzip"
aws s3 sync $DATADIR/matched/ $UKMONSHAREDBUCKET/matches/matchedpq/ --quiet --exclude "*" --include "*.snap" --exclude "*.bkp" --exclude "*.gzip"
