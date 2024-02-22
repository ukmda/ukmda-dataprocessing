#!/bin/bash
echo $(date) starting
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $here/ukmda-shared

yr=$(date +%Y)
echo $(date) singlepq
aws s3 sync s3://ukmda-shared/matches/singlepq ./matches/singlepq --exclude "*" --include "*${yr}*"
echo $(date) matchedpq
aws s3 sync s3://ukmda-shared/matches/matchedpq ./matches/matchedpq --exclude "*" --include "*${yr}*"

echo $(date) fireballs
aws s3 sync s3://ukmda-shared/fireballs ./fireballs --exclude "*" --include "${yr}/"

echo $(date) kmls
aws s3 sync s3://ukmda-shared/kmls ./kmls --quiet

echo $(date) consolidated
    aws s3 sync s3://ukmda-shared/consolidated ./consolidated --exclude "*" --include "*${yr}*" --exclude "temp/*" 

echo $(date) RMSCorrelate
aws s3 sync s3://ukmda-shared/matches/RMSCorrelate ./matches/RMSCorrelate --exclude "*" --include "*_${yr}*"

echo $(date) done

# note that backupOldData.py is a one-off to collect data scattered in the old Archive area and should not be rerun.
