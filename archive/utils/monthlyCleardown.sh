#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# script to backup then clear down orbits from the local disk. 

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

what=$1
if [ "$what" == "" ] ; then
    echo "usage: ./monthlyCleardown.sh single|raw|matched|reports|search|other"
    exit
fi 

cyr=$(date +%Y)
cmt=$(date +%m)
lyr=$(date --date='last year' +%Y)
lym=$(date --date='last month' +%Y%m)

mkdir -p $DATADIR/olddata

# SINGLE STATION DATA
case "$what" in 
single)
    logger -s -t monthlyClearDown "single-station data"
    cd $DATADIR/single/new/processed
    # backup then remove last year's data if still present
    if compgen -G "$DATADIR/single/new/processed/ukmon*_${lyr}????_*.csv" > /dev/null ; then 
        if [ ! -f $DATADIR/olddata/${lyr}-singlecsv.tar ] ; then 
            tar cvf $DATADIR/olddata/${lyr}-singlecsv.tar ukmon*_${lyr}????_*.csv
        else
            tar uvf $DATADIR/olddata/${lyr}-singlecsv.tar ukmon*_${lyr}????_*.csv
        fi
        rm -f $DATADIR/single/new/processed/ukmon*_${lyr}????_*.csv
    else
        echo "no ukmon-csv files from ${lyr} to archive"
    fi 
    # backup last month's data 
    if compgen -G "$DATADIR/single/new/processed/ukmon*_${lym}??_*.csv" > /dev/null ; then 
        if [ $cmt -ne 1 ] ; then 
            if [ ! -f $DATADIR/olddata/${lym}-singlecsv.tar ] ; then 
                tar cvf $DATADIR/olddata/${lym}-singlecsv.tar ukmon*_${lym}??_*.csv
            else
                tar uvf $DATADIR/olddata/${lym}-singlecsv.tar ukmon*_${lym}??_*.csv
            fi
        fi
        rm -f $DATADIR/single/new/processed/ukmon*_${lym}??_*.csv
    else
        echo "no ukmon-csv files from ${lym} to archive"
    fi
    ;; 
raw)
    logger -s -t monthlyClearDown "rawcsv data"
    # raw CSV files from cameras
    cd $DATADIR/single/rawcsvs
    # backup then remove last year's data if still present
    if compgen -G "$DATADIR/single/rawcsvs/*${lyr}????_??????_*.csv" > /dev/null ; then 
        if [ ! -f $DATADIR/olddata/${lyr}-rawcsv.tar ] ; then 
            tar cvf $DATADIR/olddata/${lyr}-rawcsv.tar *${lyr}????_??????_*.csv
        else
            tar uvf $DATADIR/olddata/${lyr}-rawcsv.tar *${lyr}????_??????_*.csv
        fi
        find . -maxdepth 1 -name "*${lyr}????_??????_*.csv" -print0 | xargs -0 rm -f
    else
        echo "no rawcsv files from ${lyr} to archive"
    fi 
    # backup last month's data 
    if compgen -G "$DATADIR/single/rawcsvs/*${lym}??_??????_*.csv" > /dev/null ; then 
        if [ ! -f $DATADIR/olddata/${lyr}-rawcsv.tar ] ; then 
            tar cvf $DATADIR/olddata/${lyr}-rawcsv.tar *${lym}??_??????_*.csv
        else
            tar uvf $DATADIR/olddata/${lyr}-rawcsv.tar *${lym}??_??????_*.csv
        fi
        rm -f $DATADIR/single/rawcsvs/*${lym}??_??????_*.csv
    else
        echo "no rawcsv files from ${lym} to archive"
    fi 
    ;;
matched)
    logger -s -t monthlyClearDown "match data"
    # MATCHES
    # last year's fullcsv files
    cd $DATADIR/orbits/$lyr/fullcsv/processed
    if compgen -G "$DATADIR/orbits/${lyr}/fullcsv/processed/${lyr}*.csv" > /dev/null ; then 
        if [ ! -f $DATADIR/olddata/${lyr}-matchfullcsv.tar ] ; then 
            tar cvf $DATADIR/olddata/${lyr}-matchfullcsv.tar ${lyr}*.csv
        else
            tar uvf $DATADIR/olddata/${lyr}-matchfullcsv.tar ${lyr}*.csv
        fi
        rm -f $DATADIR/orbits/${lyr}/fullcsv/processed/${lyr}*.csv
    else
        echo "no fullcsv files from ${lyr} to archive"
    fi

    # and now last months fullcsv data
    cd $DATADIR/orbits/$cyr/fullcsv/processed
    if compgen -G "$DATADIR/orbits/${cyr}/fullcsv/processed/${lym}??-*.csv" > /dev/null ; then 
        if [ ! -f $DATADIR/olddata/${lym}-matchfullcsv.tar ] ; then 
            tar cvf $DATADIR/olddata/${lym}-matchfullcsv.tar ${lym}??-*.csv
        else
            tar uvf $DATADIR/olddata/${lym}-matchfullcsv.tar ${lym}??-*.csv
        fi
        rm -f $DATADIR/orbits/${cyr}/fullcsv/processed/${lym}??-*.csv
    else
        echo "no fullcsv files from ${lym} to archive"
    fi
    ;;
reports)
    logger -s -t monthlyClearDown "reports and so forth"
    # SHOWER, MONTHLY AND ANNUAL REPORTS FROM PREVIOUS YEAR
    cd $DATADIR/reports/${lyr}
    nf=$(ls -1 | wc -l)
    if [ $nf -ne 0 ] ; then 
        if [ ! -f $DATADIR/olddata/${lyr}reports.tar ] ; then 
            tar cvf $DATADIR/olddata/${lyr}-reports.tar *
        else
            tar uvf $DATADIR/olddata/${lyr}-reports.tar *
        fi
        rm -Rf *
    else
        echo "no report files from ${lyr} to archive"
    fi
    ;;
search)
    logger -s -t monthlyClearDown "old search indexes"
    # SEARCH INDEXES FOR PRIOR YEAR
    cd $DATADIR/searchidx 
    if compgen -G "$DATADIR/searchidx/${lyr}-allevents.csv" > /dev/null ; then 
        if [ ! -f $DATADIR/olddata/${lyr}-searchidx.tar ] ; then 
            tar cvf $DATADIR/olddata/${lyr}-searchidx.tar ${lyr}-allevents.csv
        else
            tar uvf $DATADIR/olddata/${lyr}-searchidx.tar ${lyr}-allevents.csv
        fi
        rm -Rf $DATADIR/searchidx/${lyr}-allevents.csv
    else
        echo "no search indexes from ${lyr} to archive"
    fi
    ;;
ftpdata)
    logger -s -t monthlyClearDown "old ftpdetect and platepars_all files"
    # cleardown the raw input data. This is already backed up elsewhere
    inputym=$(date --date='3 months ago' +%Y%m)
    #python $PYLIB/maintenance/dataMaintenance.py $inputym
    ;;
*)
    echo missing argument
    ;;
esac     
# now push it all to the offline backup
logger -s -t monthlyClearDown "syncing to backup bucket"
aws s3 sync $DATADIR/olddata/ s3://ukmda-admin/backups/ --exclude "*" --include "${lyr}*.tar" --quiet
rm -f $DATADIR/olddata/${lyr}*.tar

aws s3 sync $DATADIR/olddata/ s3://ukmda-admin/backups/ --exclude "*" --include "${lym}*.tar" --quiet
# dont do this in case data arrives late
#rm -f $DATADIR/olddata/${lym}*.tar
