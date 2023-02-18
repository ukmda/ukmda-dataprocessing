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
    if [ ! -f $DATADIR/olddata/${lyr}-singlecsv.tar.gz ] ; then 
        tar cvfz $DATADIR/olddata/${lyr}-singlecsv.tar.gz ukmon*_${lyr}????_*.csv
    else
        gunzip $DATADIR/olddata/${lyr}-singlecsv.tar.gz
        tar uvf $DATADIR/olddata/${lyr}-singlecsv.tar ukmon*_${lyr}????_*.csv
        gzip $DATADIR/olddata/${lyr}-singlecsv.tar
    fi
    rm -f ukmon*_${lyr}????_*.csv
else
    echo "no ukmon-csv files from ${lyr} to archive"
fi 
# backup last month's data 
if compgen -G "$DATADIR/single/new/processed/ukmon*_${lym}??_*.csv" > /dev/null ; then 
    if [ $cmt -ne 1 ] ; then 
        if [ ! -f $DATADIR/olddata/${cyr}-singlecsv.tar.gz ] ; then 
            tar cvfz $DATADIR/olddata/${cyr}-singlecsv.tar.gz ukmon*_${lym}??_*.csv
        else
            gunzip $DATADIR/olddata/${cyr}-singlecsv.tar.gz
            tar uvf $DATADIR/olddata/${cyr}-singlecsv.tar ukmon*_${lym}??_*.csv
            gzip $DATADIR/olddata/${cyr}-singlecsv.tar
        fi
    fi
    rm -f ukmon*_${lym}*.csv 
else
    echo "no ukmon-csv files from ${lym} to archive"
fi

# MATCHES
# last year's fullcsv files
cd $DATADIR/orbits/$lyr/fullcsv/processed
if compgen -G "$DATADIR/orbits/${lyr}/fullcsv/processed/${lyr}*.csv" > /dev/null ; then 
    if [ ! -f $DATADIR/olddata/${lyr}-matchfullcsv.tar.gz ] ; then 
        tar cvfz $DATADIR/olddata/${lyr}-matchfullcsv.tar.gz ${lyr}*.csv
    else
        gunzip $DATADIR/olddata/${lyr}-matchfullcsv.tar.gz
        tar uvf $DATADIR/olddata/${lyr}-matchfullcsv.tar ${lyr}*.csv
        gzip $DATADIR/olddata/${lyr}-matchfullcsv.tar
    fi
    rm -f *.csv 
else
    echo "no fullcsv files from ${lyr} to archive"
fi

# and now last months fullcsv data
cd $DATADIR/orbits/$cyr/fullcsv/processed
if compgen -G "$DATADIR/orbits/${cyr}/fullcsv/processed/${lym}??-*.csv" > /dev/null ; then 
    if [ ! -f $DATADIR/olddata/${cyr}-matchfullcsv.tar.gz ] ; then 
        tar cvfz $DATADIR/olddata/${cyr}-matchfullcsv.tar.gz ${lym}??-*.csv
    else
        gunzip $DATADIR/olddata/${cyr}-matchfullcsv.tar.gz
        tar uvf $DATADIR/olddata/${cyr}-matchfullcsv.tar ${lym}??-*.csv
        gzip $DATADIR/olddata/${cyr}-matchfullcsv.tar.gz
    fi
    rm -f ${lym}??-*.csv 
else
    echo "no fullcsv files from ${lym} to archive"
fi

# SHOWER, MONTHLY AND ANNUAL REPORTS FROM PREVIOUS YEAR
cd $DATADIR/reports/${lyr}
nf=$(ls -1 | wc -l)
if [ $nf -ne 0 ] ; then 
    if [ ! -f $DATADIR/olddata/${lyr}reports.tar.gz ] ; then 
        tar cvfz $DATADIR/olddata/${lyr}-reports.tar.gz *
    else
        gunzip $DATADIR/olddata/${lyr}reports.tar.gz
        tar uvf $DATADIR/olddata/${lyr}-reports.tar *
        gzip $DATADIR/olddata/${lyr}reports.tar
    fi
    rm -Rf *
else
    echo "no report files from ${lyr} to archive"
fi

# SEARCH INDEXES FOR PRIOR YEAR
cd $DATADIR/searchidx 
if compgen -G "$DATADIR/searchidx/${lyr}-allevents.csv" > /dev/null ; then 
    if [ ! -f $DATADIR/olddata/${lyr}-searchidx.tar.gz ] ; then 
        tar cvfz $DATADIR/olddata/${lyr}-searchidx.tar.gz ${lyr}-allevents.csv
    else
        gunzip $DATADIR/olddata/${lyr}-searchidx.tar.gz
        tar uvf $DATADIR/olddata/${lyr}-searchidx.tar ${lyr}-allevents.csv
        gzip $DATADIR/olddata/${lyr}-searchidx.tar
    fi
    rm -Rf ${lyr}-allevents.csv
else
    echo "no search indexes from ${lyr} to archive"
fi

# now push it all to the offline backup
aws s3 sync $DATADIR/olddata/ s3://ukmon-shared-backup/analysisbackup/ --exclude "*" --include "${lyr}*.tar.gz" --quiet
rm -f $DATADIR/olddata/${lyr}*.tar.gz

aws s3 sync $DATADIR/olddata/ s3://ukmon-shared-backup/analysisbackup/ --exclude "*" --include "${lym}*.tar.gz" --quiet
# dont do this in case data arrives late
#rm -f $DATADIR/olddata/${lym}*.tar.gz