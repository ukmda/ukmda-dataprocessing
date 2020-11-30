#!/bin/bash
#
# monthly reporting for UKMON
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"


echo getting latest combined files
source ~/.ssh/ukmon-shared-keys
aws s3 sync s3://ukmon-shared/consolidated/ $here/DATA/consolidated --exclude 'consolidated/temp*'

cd $here/DATA
cp $here/UA_header.txt UFO_Merged_Files.csv
ls -1 consolidated/M* | while read i 
do
    sed '1d' $i >> UFO_Merged_Files.csv
done
cd $here
YR=`date +%Y`
$here/analyse.sh ALL $YR

