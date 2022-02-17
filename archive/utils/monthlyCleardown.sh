#!/bin/bash
#
# script to backup then clear down orbits from the local disk. 

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1
source $HOME/venvs/$WMPL_ENV/bin/activate

source ~/.ssh/ukmon-backup-keys

cyr=$(date +%Y)
cmt=$(date +%m)
lyr=$(date --date='last year' +%Y)
lym=$(date --date='last month' +%Y%m)

mkdir -p $DATADIR/olddata

# SINGLE STATION RAW DATA
cd $SRC/single/new/processed
# backup then remove last year's data if still present
if [ ! -f $DATADIR/olddata/${lyr}singlecsv.tgz ] ; then 
    tar cvfz $DATADIR/olddata/${lyr}singlecsv.tgz ukmon*_${lyr}*.csv 
else
    tar uvfz $DATADIR/olddata/${lyr}singlecsv.tgz ukmon*_${lyr}*.csv 
fi
rm -f ukmon*_${lyr}*.csv 

# other than in january, backup last month's data 
if [ $cmt -ne 1 ] ; then 
    if [ ! -f $DATADIR/olddata/${cyr}singlecsv.tgz ] ; then 
        echo tar cvfz $DATADIR/olddata/${cyr}singlecsv.tgz ukmon*_${lym}*.csv 
    else
        echo tar uvfz $DATADIR/olddata/${cyr}singlecsv.tgz ukmon*_${lym}*.csv 
    fi
fi
rm -f ukmon*_${lym}*.csv 

# SHOWER, MONTHLY AND ANNUAL REPORTS FROM PREVIOUS YEAR
cd $SRC/data/reports/${lyr}
nf=$(ls -1 | wc -l)
if [ $nf -ne 0 ] ; then 
    if [ ! -f $DATADIR/olddata/${lyr}reports.tgz ] ; then 
        tar cvfz $DATADIR/olddata/${lyr}reports.tgz *
    else
        tar uvfz $DATADIR/olddata/${lyr}reports.tgz *
    fi
    rm -Rf *
fi

# SEARCH INDEXES FOR PRIOR YEAR
cd $SRC/data/searchidx 
if [ ! -f $DATADIR/olddata/${lyr}searchidx.tgz ] ; then 
    tar cvfz $DATADIR/olddata/${lyr}searchidx.tgz ${lyr}-allevents.csv
else
    tar uvfz $DATADIR/olddata/${lyr}searchidx.tgz ${lyr}-allevents.csv
fi
rm -Rf ${lyr}-allevents.csv

source ~/.ssh/ukmon-backup-keys
aws s3 sync $DATADIR/olddata/ s3://ukmon-shared-backup/analysisbackup/ --exclude "*" --include "*.tgz" --quiet
