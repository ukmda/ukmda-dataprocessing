#!/bin/bash
#
# monthly reporting for UKMON
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $HOME/src/config/config.ini >/dev/null 2>&1

yr=$2
shwr=$1
lastyr=$((yr-1))

echo getting latest combined files

source ~/.ssh/ukmon-shared-keys
aws s3 sync s3://ukmon-shared/consolidated/ $here/DATA/consolidated --exclude 'consolidated/temp/*'

cd $here/DATA
echo "Getting single detections and associations for $yr"
cp consolidated/M_${yr}-unified.csv UKMON-all-single.csv
cp consolidated/P_${yr}-unified.csv RMS_Merged_Files.csv

echo "getting RMS single-station shower associations for $yr"
echo "ID,Y,M,D,h,m,s,Shwr" > RMS_Single_Assocs.csv
cat $REPORTDIR/consolidated/A/??????_${yr}* >> RMS_Single_Assocs.csv

echo "getting matched detections for $yr"
cp $here/templates/UO_header.txt $here/DATA/matched/matches-$yr.csv
cat $REPORTDIR/matches/$yr/csv/$yr*.csv >> $here/DATA/matched/matches-$yr.csv

if [ "$shwr" == "QUA" ] ; then
    echo "including previous year to catch early Quadrantids"
    sed '1d' consolidated/M_${lastyr}-unified.csv >> UKMON-all-single.csv
    sed '1d' consolidated/P_${lastyr}-unified.csv >> RMS_Merged_Files.csv

    echo "including prev year RMS single-station shower associations"
    cat $REPORTDIR/consolidated/A/??????_${lastyr}* >> RMS_Single_Assocs.csv

    echo "getting matched detections for $lastyr"
    cp $here/templates/UO_header.txt $here/DATA/matched/matches-$lastyr.csv
    cat $REPORTDIR/matches/$lastyr/csv/$lastyr*.csv >> $here/DATA/matched/matches-$lastyr.csv

else
    echo "" >> UKMON-all-single.csv
    echo "" >> RMS_Merged_Files.csv
    # not needed for these data echo "" >> RMS_Single_Assocs.csv
fi 
echo "got relevant data"

lc=$(wc -l $here/DATA/matched/matches-$yr.csv | awk '{print $1}')
if [ $lc -gt 1 ] ; then
    cp $here/DATA/matched/matches-$yr.csv $here/DATA/UKMON-all-matches.csv
else
    cp $here/DATA/matched/pre2020/matches-$yr.csv $here/DATA/UKMON-all-matches.csv
fi 

if [ "$shwr" == "QUA" ] ; then
    lc=$(wc -l $here/DATA/matched/matches-$lastyr.csv | awk '{print $1}')
    if [ $lc -gt 1 ] ; then
        sed '1d' $here/DATA/matched/matches-$lastyr.csv >> $here/DATA/UKMON-all-matches.csv
    else
        sed '1d' $here/DATA/matched/pre2020/matches-$yr.csv >> $here/DATA/UKMON-all-matches.csv
    fi 
fi 

cd $here
echo "running $shwr report for $yr"
$here/createReport.sh $shwr $yr $3

