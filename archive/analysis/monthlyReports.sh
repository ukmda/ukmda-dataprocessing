#!/bin/bash
#
# monthly reporting for UKMON
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

source $HOME/venvs/${WMPL_ENV}/bin/activate
export PYTHONPATH=$RMS_LOC:$wmpl_loc:$PYLIB

yr=$2
shwr=$1
lastyr=$((yr-1))

cd ${DATADIR}
logger -s -t monthlyReports "Backing up previous days data"

# save previous data, then extract the changes 
cp UFO-all-single.csv prv-UFO-all-single.csv
cp RMS-all-single.csv prv-RMS-all-single.csv
cp RMS-assoc-single.csv prv-RMS-assoc-single.csv
cp RMS-UFOA-single.csv prv-RMS-UFOA-single.csv
cp UKMON-all-single.csv prv-UKMON-all-single.csv

logger -s -t monthlyReports "Fetching latest data"
cp consolidated/M_${yr}-unified.csv UFO-all-single.csv
comm -1 -3 prv-UFO-all-single.csv UFO-all-single.csv > new-UFO-all-single.csv

cp consolidated/P_${yr}-unified.csv RMS-all-single.csv
comm -1 -3 prv-RMS-all-single.csv RMS-all-single.csv > new-RMS-all-single.csv

logger -s -t monthlyReports "getting RMS single-station shower associations for $yr"
echo "ID,Y,M,D,h,m,s,Shwr" > RMS-assoc-single.csv
cat ${DATADIR}/consolidated/A/??????_${yr}* >> RMS-assoc-single.csv
comm -1 -3 prv-RMS-assoc-single.csv RMS-assoc-single.csv > new-RMS-assoc-single.csv

logger -s -t monthlyReports "getting matched detections for $yr"
cp $here/templates/UO_header.txt ${DATADIR}/matched/matches-$yr.csv
cat ${DATADIR}/orbits/$yr/csv/$yr*.csv >> ${DATADIR}/matched/matches-$yr.csv

echo "" >> UFO-all-single.csv
echo "" >> RMS-all-single.csv

logger -s -t monthlyReports "merge in the RMS data"
l1=$(wc -l new-RMS-all-single.csv | awk '{print $1}')
l2=$(wc -l new-RMS-assoc-single.csv | awk '{print $1}')

if [[ l1 -gt 0  && l2 -gt 0 ]] ; then
    python $PYLIB/converters/RMStoUFOA.py new-RMS-all-single.csv new-RMS-assoc-single.csv new-RMS-UFOA-single.csv $SRC/analysis/templates/
    sed '1d' new-RMS-UFOA-single.csv >> UKMON-all-single.csv
    cp UKMON-all-single.csv consolidated/UKMON-${yr}-single.csv

    sed '1d' new-RMS-UFOA-single.csv >> RMS-UFOA-single.csv
    cp RMS-UFOA-single.csv consolidated/R_${yr}-unified.csv
fi

logger -s -t monthlyReports "got relevant data, copying to target"

cd $here
logger -s -t monthlyReports "running $shwr report for $yr"

$here/createReport.sh $shwr $yr $3

logger -s -t monthlyReports "shower report done"

