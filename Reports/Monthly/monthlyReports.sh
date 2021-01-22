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

source $here/../orbits/orbitsolver.ini >/dev/null 2>&1
YR=$2
SHWR=$1

cp $here/UO_header.txt $here/DATA/matched/matches-$YR.csv
cat $results/$YR/orbits/csv/$YR*.csv >> $here/DATA/matched/matches-$YR.csv
lc=$(wc -l $here/DATA/matched/matches-$YR.csv | awk '{print $1}')
if [ $lc -gt 1 ] ; then
    cp $here/DATA/matched/matches-$YR.csv $here/DATA/UKMON-all-matches.csv
else
    cp $here/DATA/matched/pre2020/matches-$YR.csv $here/DATA/UKMON-all-matches.csv
fi 

cd $here
$here/createReport.sh $SHWR $YR $3

