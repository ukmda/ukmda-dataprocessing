#!/bin/bash
echo $(date) starting
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $here/ukmda-shared

yr=$(date +%Y)
echo $(date) singlepq
aws s3 sync s3://ukmda-shared/matches/singlepq ./matches/singlepq
echo $(date) matchedpq
aws s3 sync s3://ukmda-shared/matches/matchedpq ./matches/matchedpq
echo $(date) fireballs

aws s3 sync s3://ukmda-shared/fireballs ./fireballs
echo $(date) kmls

aws s3 sync s3://ukmda-shared/kmls ./kmls
echo $(date) consolidated

aws s3 sync s3://ukmda-shared/consolidated ./consolidated --exclude "temp/*"
echo $(date) RMSCorrelate

aws s3 sync s3://ukmda-shared/matches/RMSCorrelate ./matches/RMSCorrelate --exclude "*" --include "*${yr}*"

echo $(date) done

