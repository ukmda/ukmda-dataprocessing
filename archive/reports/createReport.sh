#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

if [ $# -lt 2 ] ; then
	echo Usage: createReport.sh GEM 2017 {force}
else
    logger -s -t createReport "starting"
    source /home/ec2-user/venvs/${WMPL_ENV}/bin/activate
    export PYTHONPATH=$wmpl_loc:$PYLIB

    cd ${DATADIR}

    if [[ ! -d reports/$2/$1 || "$3" == "force" ]] ; then
        logger -s -t createReport "Running the analysis routines"
        $here/runRAnalysis.sh $1 $2  > ${SRC}/logs/$1$2.log
        logger -s -t createReport "done, now reating report"
    fi
    cd ${DATADIR}
    if [ "$1" == "ALL" ]; then
        sname="All Data"
    else
        sname=`grep $1 ${RCODEDIR}/CONFIG/streamnames.csv | awk -F, '{print $2}'`
    fi
    if [ -d reports/$2/$1 ] ; then 
        logger -s -t createReport "gathering facts"
        if [ "$1" == "ALL" ]; then
            logger -s -t createReport "processing $1"
            cat $TEMPLATES/header.html $here/templates/report-template.html $TEMPLATES/footer.html > ${DATADIR}/reports/$2/$1/index.html
            metcount=$(grep "OTHER Matched" ${SRC}/logs/ALL$2.log | awk '{print $4}')
            maxalt=$(grep "_$2" ${DATADIR}/UKMON-all-matches.csv  | grep UNIFIED | awk -F, '{printf("%.1f\n",$44)}' | sort -n | tail -1)
            minalt=$(grep "_$2" ${DATADIR}/UKMON-all-matches.csv  | grep UNIFIED | awk -F, '{printf("%.1f\n", $52)}' | sort -n | head -1)
        else
            logger -s -t createReport "processing $2 $1"
            cat $TEMPLATES/header.html $here/templates/shower-report-template.html $TEMPLATES/footer.html > ${DATADIR}/reports/$2/$1/index.html
            metcount=$(sed "1d" ${DATADIR}/UKMON-all-single.csv | grep $1 | wc -l) 
            maxalt=$(grep $1 ${DATADIR}/UKMON-all-matches.csv  | grep UNIFIED | grep "_$2" | awk -F, '{printf("%.1f\n",$44)}' | sort -n | tail -1)
            minalt=$(grep $1 ${DATADIR}/UKMON-all-matches.csv  | grep UNIFIED | grep "_$2" | awk -F, '{printf("%.1f\n",$52)}' | sort -n | head -1)
        fi 

        cd reports/$2/$1

        camcount=`cat TABLE_stream_counts_by_Station.csv | wc -l`
        yr=$2
        repdate=`date '+%Y-%m-%d %H:%M:%S'`
        pairs=`grep "UNIFIED Matched" ${SRC}/logs/$1$2.log  | awk '{print $4}'`
        unifrac=`echo "scale=1;$pairs*100/$metcount" | bc`
        fbcount=`tail -n +2 TABLE_Fireballs.csv |wc -l`

        logger -s -t createReport "making tables"
        python $PYLIB/reports/makeReportTables.py $1 $2 $fbcount

        logger -s -t createReport "updating index file with facts"
        cat index.html | sed "s/__CAMCOUNT__/${camcount}/g" | sed "s/__YEAR__/${yr}/g" | \
            sed "s/__REPDATE__/${repdate}/g" | sed "s/__METCOUNT__/${metcount}/g" | \
            sed "s/__PAIRS__/${pairs}/g" | sed "s/__UNIFRAC__/${unifrac}/g" | \
            sed "s/__FBCOUNT__/${fbcount}/g" | sed "s/__MAXALT__/${maxalt}/g" | \
            sed "s/__SHWR__/${sname}/g" | \
            sed "s/__MINALT__/${minalt}/g" > tmpidx.html
            mv tmpidx.html index.html

        logger -s -t createReport "copying files to website"
        source $WEBSITEKEY
        aws s3 sync . $WEBSITEBUCKET/reports/$2/$1
        logger -s -t createReport "all done"

        ${SRC}/website/createReportIndex.sh
    fi
    logger -s -t createReport "finished"    
fi 