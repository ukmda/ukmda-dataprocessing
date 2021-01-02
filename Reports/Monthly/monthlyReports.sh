#!/bin/bash
#
# monthly reporting for UKMON
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"


echo getting latest combined files
source ~/.ssh/ukmon-shared-keys
aws s3 sync s3://ukmon-shared/consolidated/ $here/DATA/consolidated --exclude 'consolidated/temp/*'

cd $here/DATA
cp $here/UA_header.txt UKMON-all-single.csv
ls -1 consolidated/M* | while read i 
do
    sed '1d' $i >> UKMON-all-single.csv
    echo "" >> UKMON-all-single.csv
done
cp $here/RMS_header.txt RMS_Merged_Files.csv
ls -1 consolidated/P* | while read i 
do
    sed '1d' $i >> RMS_Merged_Files.csv
    echo "" >> RMS_Merged_Files.csv
done

source $here/../orbits/orbitsolver.ini
YR=`date +%Y`

cp $here/UO_header.txt $here/DATA/matched/matches-$YR.csv
cat $results/$YR/orbits/csv/$YR*.csv >> $here/DATA/matched/matches-$YR.csv
wc -l $here/DATA/matched/matches-$YR.csv
cp $here/DATA/matched/matches-$YR.csv $here/DATA/UKMON-all-matches.csv

cd $here
$here/createReport.sh ALL $YR

