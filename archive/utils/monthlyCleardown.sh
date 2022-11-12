#!/bin/bash
#
# script to backup then clear down orbits from the local disk. 

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
source $HOME/venvs/$WMPL_ENV/bin/activate

cyr=$(date +%Y)
cmt=$(date +%m)
lyr=$(date --date='last year' +%Y)
lym=$(date --date='last month' +%Y%m)

mkdir -p $DATADIR/olddata

# SINGLE STATION RAW DATA
cd $DATADIR/single/new/processed
# backup then remove last year's data if still present
if compgen -G "$DATADIR/single/new/processed/ukmon*_${lyr}????_*.csv" > /dev/null ; then 
    if [ ! -f $DATADIR/olddata/${lyr}-singlecsv.tgz ] ; then 
        tar cvfz $DATADIR/olddata/${lyr}-singlecsv.tgz ukmon*_${lyr}????_*.csv
    else
        tar uvfz $DATADIR/olddata/${lyr}-singlecsv.tgz ukmon*_${lyr}????_*.csv
    fi
    rm -f ukmon*_${lyr}????_*.csv
fi 
# backup last month's data 
if compgen -G "$DATADIR/single/new/processed/ukmon*_${lym}??_*.csv" > /dev/null ; then 
    if [ $cmt -ne 1 ] ; then 
        if [ ! -f $DATADIR/olddata/${cyr}-singlecsv.tgz ] ; then 
            tar cvfz $DATADIR/olddata/${cyr}-singlecsv.tgz ukmon*_${lym}??_*.csv
        else
            tar uvfz $DATADIR/olddata/${cyr}-singlecsv.tgz ukmon*_${lym}??_*.csv
        fi
    fi
    rm -f ukmon*_${lym}*.csv 
fi

# MATCHES
# last year's CSV, extracsv and fullcsv files
cd $DATADIR/orbits/$lyr/csv/processed
if compgen -G "$DATADIR/orbits/${lyr}/csv/processed/*.csv" > /dev/null ; then 
    if [ ! -f $DATADIR/olddata/${lyr}-matchcsv.tgz ] ; then 
        tar cvfz $DATADIR/olddata/${lyr}-matchcsv.tgz *.csv
    else
        tar uvfz $DATADIR/olddata/${lyr}-matchcsv.tgz *.csv
    fi
    rm -f *.csv 
fi
cd $DATADIR/orbits/$lyr/extracsv/processed
if compgen -G "$DATADIR/orbits/${lyr}/extracsv/processed/*.csv" > /dev/null ; then 
    if [ ! -f $DATADIR/olddata/${lyr}-matchextracsv.tgz ] ; then 
        tar cvfz $DATADIR/olddata/${lyr}-matchextracsv.tgz *.csv
    else
        tar uvfz $DATADIR/olddata/${lyr}-matchextracsv.tgz *.csv
    fi
    rm -f *.csv 
fi
cd $DATADIR/orbits/$lyr/fullcsv/processed
if compgen -G "$DATADIR/orbits/${lyr}/fullcsv/processed/*.csv" > /dev/null ; then 
    if [ ! -f $DATADIR/olddata/${lyr}-matchfullcsv.tgz ] ; then 
        tar cvfz $DATADIR/olddata/${lyr}-matchfullcsv.tgz *.csv
    else
        tar uvfz $DATADIR/olddata/${lyr}-matchfullcsv.tgz *.csv
    fi
    rm -f *.csv 
fi

# and now last months fullcsv data
cd $DATADIR/orbits/$cyr/fullcsv/processed
if compgen -G "$DATADIR/orbits/${cyr}/fullcsv/processed/${lym}??-*.csv" > /dev/null ; then 
    if [ ! -f $DATADIR/olddata/${cyr}-matchfullcsv.tgz ] ; then 
        tar cvfz $DATADIR/olddata/${cyr}-matchfullcsv.tgz ${lym}??-*.csv
    else
        tar uvfz $DATADIR/olddata/${cyr}-matchfullcsv.tgz ${lym}??-*.csv
    fi
    #rm -f ${lym}??-*.csv 
fi

# SHOWER, MONTHLY AND ANNUAL REPORTS FROM PREVIOUS YEAR
cd $DATADIR/reports/${lyr}
nf=$(ls -1 | wc -l)
if [ $nf -ne 0 ] ; then 
    if [ ! -f $DATADIR/olddata/${lyr}reports.tgz ] ; then 
        tar cvfz $DATADIR/olddata/${lyr}-reports.tgz *
    else
        tar uvfz $DATADIR/olddata/${lyr}-reports.tgz *
    fi
    rm -Rf *
fi

# SEARCH INDEXES FOR PRIOR YEAR
cd $DATADIR/searchidx 
if compgen -G "$DATADIR/searchidx/${lyr}-allevents.csv" > /dev/null ; then 
    if [ ! -f $DATADIR/olddata/${lyr}-searchidx.tgz ] ; then 
        tar cvfz $DATADIR/olddata/${lyr}-searchidx.tgz ${lyr}-allevents.csv
    else
        tar uvfz $DATADIR/olddata/${lyr}-searchidx.tgz ${lyr}-allevents.csv
    fi
    rm -Rf ${lyr}-allevents.csv
fi

# now push it all to the offline backup
aws s3 sync $DATADIR/olddata/ s3://ukmon-shared-backup/analysisbackup/ --exclude "*" --include "*.tgz" --quiet
