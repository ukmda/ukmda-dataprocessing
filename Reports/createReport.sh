#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

if [ $# -lt 2 ] ; then
	echo Usage: createReport.sh GEM 2017
else
    source $here/config.ini >/dev/null 2>&1
    source /home/ec2-user/venvs/wmpl/bin/activate
    if [ ! -d $REPORTDIR/$2/$1 ] ; then 
        $here/analyse.sh $1 $2 
    fi

    if [ "$2" == "ALL" ]; then
        cp $here/report-template.shtml $REPORTDIR/$2/$1/index.shtml
        metcount=`cat $here/DATA/consolidated/M_${2}-unified.csv | wc -l`
        maxalt=`grep "_$2" $here/DATA/UKMON-all-unified.csv  | grep UNIFIED | awk -F, '{print $44}' | sort -n | tail -1`
        minalt=`grep "_$2" $here/DATA/UKMON-all-unified.csv  | grep UNIFIED | awk -F, '{print $52}' | sort -n | head -1`
    else
        cp $here/shower-report-template.shtml $REPORTDIR/$2/$1/index.shtml
        metcount=`cat $here/DATA/consolidated/M_${2}-unified.csv | grep $1 | wc -l`
        maxalt=`grep $1 $here/DATA/UKMON-all-unified.csv  | grep UNIFIED | grep "_$2" | awk -F, '{print $44}' | sort -n | tail -1`
        minalt=`grep $1 $here/DATA/UKMON-all-unified.csv  | grep UNIFIED | grep "_$2" | awk -F, '{print $52}' | sort -n | head -1`
        echo $metcount $maxalt $minalt
    fi 

    cd $REPORTDIR/$2/$1

    camcount=`cat TABLE_stream_counts_by_Station.csv | wc -l`
    yr=$2
    repdate=`date '+%Y-%m-%d %H:%M:%S'`
    pairs=`cat TABLE_stream_counts.csv | awk -F, '{print $3}' | awk '{ sum += $1 } END { print sum }'`
    unifrac=`echo "scale=1;$pairs*100/$metcount" | bc`
    fbcount=`tail -n +2 TABLE_Fireballs.csv |wc -l`

    python $here/makeReportTables.py $1 $2

    cat index.shtml | sed "s/__CAMCOUNT__/${camcount}/g" | sed "s/__YEAR__/${yr}/g" | \
        sed "s/__REPDATE__/${repdate}/g" | sed "s/__METCOUNT__/${metcount}/g" | \
        sed "s/__PAIRS__/${pairs}/g" | sed "s/__UNIFRAC__/${unifrac}/g" | \
        sed "s/__FBCOUNT__/${fbcount}/g" | sed "s/__MAXALT__/${maxalt}/g" | \
        sed "s/__SHWR__/${1}/g" | \
        sed "s/__MINALT__/${minalt}/g" > tmpidx.shtml
        mv tmpidx.shtml index.shtml
fi