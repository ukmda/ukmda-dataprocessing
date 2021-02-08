#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $HOME/src/config/config.ini >/dev/null 2>&1

if [ $# -lt 2 ] ; then
	echo Usage: createReport.sh GEM 2017 {force}
else
    source /home/ec2-user/venvs/wmpl/bin/activate
    if [[ ! -d $here/REPORTS/$2/$1 || "$3" == "force" ]] ; then
        echo "Running the analysis routines"
        cd $here
        $here/analyse.sh $1 $2  > $here/logs/$1$2.log
        echo "done. Creating report"
    fi
    if [ "$1" == "ALL" ]; then
        sname="All Data"
    else
        sname=`grep $1 $CONFIG/streamnames.csv | awk -F, '{print $2}'`
    fi
    if [ -d $here/REPORTS/$2/$1 ] ; then 
        echo "gathering facts"
        if [ "$1" == "ALL" ]; then
            echo "processing $1"
            cat $TEMPLATES/header.html $here/templates/report-template.html $TEMPLATES/footer.html > $here/REPORTS/$2/$1/index.html
            metcount=$(sed "1d" $here/DATA/UKMON-all-single.csv | wc -l) 
            #metcount=`cat $here/DATA/consolidated/M_${2}-unified.csv | wc -l`
            maxalt=$(grep "_$2" $here/DATA/UKMON-all-matches.csv  | grep UNIFIED | awk -F, '{printf("%.1f\n",$44)}' | sort -n | tail -1)
            minalt=$(grep "_$2" $here/DATA/UKMON-all-matches.csv  | grep UNIFIED | awk -F, '{printf("%.1f\n", $52)}' | sort -n | head -1)
        else
            echo "processing $2 $1"
            cat $TEMPLATES/header.html $here/templates/shower-report-template.html $TEMPLATES/footer.html > $here/REPORTS/$2/$1/index.html
            metcount=$(sed "1d" $here/DATA/UKMON-all-single.csv | grep $1 | wc -l) 
            #metcount=`cat $here/DATA/consolidated/M_${2}-unified.csv | grep $1 | wc -l`
            maxalt=$(grep $1 $here/DATA/UKMON-all-matches.csv  | grep UNIFIED | grep "_$2" | awk -F, '{printf("%.1f\n",$44)}' | sort -n | tail -1)
            minalt=$(grep $1 $here/DATA/UKMON-all-matches.csv  | grep UNIFIED | grep "_$2" | awk -F, '{printf("%.1f\n",$52)}' | sort -n | head -1)
        fi 

        cd $here/REPORTS/$2/$1

        camcount=`cat TABLE_stream_counts_by_Station.csv | wc -l`
        yr=$2
        repdate=`date '+%Y-%m-%d %H:%M:%S'`
        pairs=`grep "UNIFIED Matched" $here/logs/$1$2.log  | awk '{print $4}'`
        unifrac=`echo "scale=1;$pairs*100/$metcount" | bc`
        fbcount=`tail -n +2 TABLE_Fireballs.csv |wc -l`

        echo "making tables"
        python $here/makeReportTables.py $1 $2 $fbcount

        echo "updating index file with facts"
        cat index.html | sed "s/__CAMCOUNT__/${camcount}/g" | sed "s/__YEAR__/${yr}/g" | \
            sed "s/__REPDATE__/${repdate}/g" | sed "s/__METCOUNT__/${metcount}/g" | \
            sed "s/__PAIRS__/${pairs}/g" | sed "s/__UNIFRAC__/${unifrac}/g" | \
            sed "s/__FBCOUNT__/${fbcount}/g" | sed "s/__MAXALT__/${maxalt}/g" | \
            sed "s/__SHWR__/${sname}/g" | \
            sed "s/__MINALT__/${minalt}/g" > tmpidx.html
            mv tmpidx.html index.html

        echo "copying files to website"
        source $WEBSITEKEY
        aws s3 sync . $WEBSITEBUCKET/reports/$2/$1
        echo "all done"

        ${SRC}/website/createReportIndex.sh
    fi
fi 
