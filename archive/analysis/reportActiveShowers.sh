#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# Creates a report for each currently active shower in a particular year
#
# Parameters
#   the year to process in yyyy format
#
# Consumes
#   The single and matched data from $DATADIR/single and $DATADIR/matched
#   The IAU shower database in $WMPL_LOC/wmpl/share
#
# Produces
#   A report per shower with diagrams and tables, in $DATADIR/reports/yyyy
#    which is also synced to the website

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

logger -s -t $(basename $0 .sh) "starting"

if [ $# -eq 0 ]; then
    yr=$(date +%Y)
    rundt=$(date +%Y%m%d)
else
    yr=$1
    rundt=${1}$(date +%m%d)
fi

logger -s -t $(basename $0 .sh) "start reportActiveShowers"
python -m reports.reportActiveShowers

python -c "from utils.getActiveShowers import getActiveShowers;getActiveShowers('$rundt', inclMinor=False)" | while read shwr
do 
    aws s3 sync $DATADIR/reports/${yr}/$shwr $WEBSITEBUCKET/reports/${yr}/${shwr} --quiet 
done
logger -s -t $(basename $0 .sh) "updating annual index"
${SRC}/website/createReportIndex.sh ${yr}

python -m analysis.summaryAnalysis ${yr}
aws s3 sync $DATADIR/reports/${yr}/showers $WEBSITEBUCKET/reports/${yr}/showers --quiet

logger -s -t $(basename $0 .sh) "finished"