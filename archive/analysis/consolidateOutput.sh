#!/bin/bash
#
# monthly reporting for UKMON
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

source $HOME/venvs/${WMPL_ENV}/bin/activate
export PYTHONPATH=$RMS_LOC:$wmpl_loc:$PYLIB

yr=$1

cd ${DATADIR}
logger -s -t consolidateOutput "Backing up previous days data"

# save previous data, then extract the changes 
cp UFO-all-single.csv prv-UFO-all-single.csv
cp RMS-all-single.csv prv-RMS-all-single.csv
cp RMS-assoc-single.csv prv-RMS-assoc-single.csv
cp RMS-UFOA-single.csv prv-RMS-UFOA-single.csv
cp UKMON-all-single.csv prv-UKMON-all-single.csv

logger -s -t consolidateOutput "Fetching latest data"
cp consolidated/M_${yr}-unified.csv UFO-all-single.csv
cp consolidated/P_${yr}-unified.csv RMS-all-single.csv
echo "ID,Y,M,D,h,m,s,Shwr" > RMS-assoc-single.csv
cat ${DATADIR}/consolidated/A/??????_${yr}* >> RMS-assoc-single.csv

logger -s -t consolidateOutput "getting matched detections for $yr"
if [ ! -f ${DATADIR}/matched/matches-$yr.csv ] ; then 
    cp $here/templates/UO_header.txt ${DATADIR}/matched/matches-$yr.csv
    mkdir ${DATADIR}/orbits/${yr}/csv/processed > /dev/null 2>&1
fi
cat ${DATADIR}/orbits/$yr/csv/$yr*.csv >> ${DATADIR}/matched/matches-$yr.csv
mv ${DATADIR}/orbits/$yr/csv/$yr*.csv ${DATADIR}/orbits/${yr}/csv/processed

logger -s -t consolidateOutput "getting extra orbit data for $yr"
if [ ! -f ${DATADIR}/matched/matches-extras-$yr.csv ] ; then 
    cp $here/templates/extracsv.txt ${DATADIR}/matched/matches-extras-$yr.csv
    mkdir ${DATADIR}/orbits/${yr}/extracsv/processed > /dev/null 2>&1
fi
cat ${DATADIR}/orbits/$yr/extracsv/$yr*.csv >> ${DATADIR}/matched/matches-extras-$yr.csv
mv ${DATADIR}/orbits/$yr/extracsv/$yr*.csv ${DATADIR}/orbits/${yr}/extracsv/processed

logger -s -t consolidateOutput "identify new UFO data and add it on"
comm -1 -3 prv-UFO-all-single.csv UFO-all-single.csv > new-UFO-all-single.csv
cat new-UFO-all-single.csv >> UKMON-all-single.csv

logger -s -t consolidateOutput "identify new RMS data"
comm -1 -3 prv-RMS-all-single.csv RMS-all-single.csv > new-RMS-all-single.csv
comm -1 -3 prv-RMS-assoc-single.csv RMS-assoc-single.csv > new-RMS-assoc-single.csv

echo "" >> UFO-all-single.csv
echo "" >> RMS-all-single.csv

logger -s -t consolidateOutput "merge in the RMS data"
l1=$(wc -l new-RMS-all-single.csv | awk '{print $1}')
l2=$(wc -l new-RMS-assoc-single.csv | awk '{print $1}')

if [[ l1 -gt 0  && l2 -gt 0 ]] ; then
    python $PYLIB/converters/RMStoUFOA.py new-RMS-all-single.csv new-RMS-assoc-single.csv new-RMS-UFOA-single.csv $SRC/analysis/templates/
    sed '1d' new-RMS-UFOA-single.csv >> UKMON-all-single.csv
    cp UKMON-all-single.csv consolidated/UKMON-${yr}-single.csv

    sed '1d' new-RMS-UFOA-single.csv >> RMS-UFOA-single.csv
    cp RMS-UFOA-single.csv consolidated/R_${yr}-unified.csv
fi

logger -s -t consolidateOutput "consolidation done"
