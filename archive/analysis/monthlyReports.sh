#!/bin/bash
#
# monthly reporting for UKMON
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

source $HOME/venvs/${RMS_ENV}/bin/activate
export PYTHONPATH=$RMS_LOC:$wmpl_loc:$PYLIB

yr=$2
shwr=$1
lastyr=$((yr-1))

logger -s -t monthlyReports "getting latest combined files"

source ~/.ssh/ukmon-shared-keys
aws s3 sync s3://ukmon-shared/consolidated/ ${DATADIR}/consolidated --exclude 'consolidated/temp/*'
aws s3 sync s3://ukmon-live/ ${DATADIR}/ukmonlive/ --exclude "*" --include "*.csv"

cd ${DATADIR}
logger -s -t monthlyReports "Getting single detections and associations for $yr"
cp consolidated/M_${yr}-unified.csv UFO-all-single.csv
cp consolidated/P_${yr}-unified.csv RMS-all-single.csv

logger -s -t monthlyReports "getting RMS single-station shower associations for $yr"
echo "ID,Y,M,D,h,m,s,Shwr" > RMS-assoc-single.csv
cat ${DATADIR}/consolidated/A/??????_${yr}* >> RMS-assoc-single.csv

logger -s -t monthlyReports "getting matched detections for $yr"
cp $here/templates/UO_header.txt ${DATADIR}/matched/matches-$yr.csv
cat ${DATADIR}/orbits/$yr/csv/$yr*.csv >> ${DATADIR}/matched/matches-$yr.csv

if [ "$shwr" == "QUA" ] ; then
    logger -s -t monthlyReports "including previous year to catch early Quadrantids"
    sed '1d' consolidated/M_${lastyr}-unified.csv >> UFO-all-single.csv
    sed '1d' consolidated/P_${lastyr}-unified.csv >> RMS-all-single.csv

    logger -s -t monthlyReports "including prev year RMS single-station shower associations"
    cat ${DATADIR}/consolidated/A/??????_${lastyr}* >> RMS-assoc-single.csv

    logger -s -t monthlyReports "getting matched detections for $lastyr"
    cp $here/templates/UO_header.txt ${DATADIR}/matched/matches-$lastyr.csv
    cat ${DATADIR}/orbits/$lastyr/csv/$lastyr*.csv >> ${DATADIR}/matched/matches-$lastyr.csv

else
    echo "" >> UFO-all-single.csv
    echo "" >> RMS-all-single.csv
    # not needed for these data echo "" >> RMS-assoc-single.csv
fi 
logger -s -t monthlyReports "merge in the RMS data"

cp UFO-all-single.csv UKMON-all-single.csv
python $PYLIB/converters/RMStoUFOA.py $SRC/config/config.ini RMS-all-single.csv RMS-assoc-single.csv RMS-UFOA-single.csv $SRC/analysis/templates/
sed '1d' RMS-UFOA-single.csv | sed '1d' >> UKMON-all-single.csv
cp RMS-UFOA-single.csv consolidated/R_${yr}-unified.csv
cp UKMON-all-single.csv consolidated/UKMON-${yr}-single.csv

logger -s -t monthlyReports "got relevant data, copying to target"

lc=$(wc -l ${DATADIR}/matched/matches-$yr.csv | awk '{print $1}')
if [ $lc -gt 1 ] ; then
    cp ${DATADIR}/matched/matches-$yr.csv ${DATADIR}/UKMON-all-matches.csv
else
    cp ${DATADIR}/matched/pre2020/matches-$yr.csv ${DATADIR}/UKMON-all-matches.csv
fi 

if [ "$shwr" == "QUA" ] ; then
    lc=$(wc -l ${DATADIR}/matched/matches-$lastyr.csv | awk '{print $1}')
    if [ $lc -gt 1 ] ; then
        sed '1d' ${DATADIR}/matched/matches-$lastyr.csv >> ${DATADIR}/UKMON-all-matches.csv
    else
        sed '1d' ${DATADIR}/matched/pre2020/matches-$yr.csv >> ${DATADIR}/UKMON-all-matches.csv
    fi 
fi 

cd $here
logger -s -t monthlyReports "running $shwr report for $yr"

$here/createReport.sh $shwr $yr $3

logger -s -t monthlyReports "shower report done"

