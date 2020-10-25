#!/bin/bash
#
# monthly reporting for UKMON
#
here=`pwd`/`dirname $0`

cd $here
echo getting latest combined files
source ~/.ssh/ukmon-shared-keys
aws s3 sync s3://ukmon-shared/consolidated/ $here/DATA/consolidated --exclude 'consolidated/temp*'

cd DATA
cp ../UA_header.txt UFO_Merged_Files.csv
ls -1 consolidated/M* | while read i 
do
    sed '1d' $i >> UFO_Merged_Files.csv
done
cd ..
YR=`date +%Y`
./analyse.sh ALL $YR

