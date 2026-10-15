#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# script to back up the match, single and individual datasets

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

logger -s -t $(basename $0 .sh) "starting"

# dates to process for
arcdate=$( date --date "180 days ago" +%Y%m)
bkpdate=$(date +%Y%m)
yr=$(date +%Y)

BKPBUCKET="s3://ukmda-admin/backups/mthly"

logger -s -t $(basename $0 .sh) "archiving singles and matches parquet files"
aws s3 cp ${DATADIR}/matched/matches-full-${yr}.parquet.snap ${BKPBUCKET}/matches-full-${yr}.parquet.snap.${bkpdate}
aws s3 cp ${DATADIR}/single/singles-${yr}.parquet.snap ${BKPBUCKET}/singles-${yr}.parquet.snap.${bkpdate}

logger -s -t $(basename $0 .sh) "archiving matched CSVs"
cd $DATADIR/orbits/${yr}/fullcsv/processed
mkdir tmp
cd tmp
find .. -mtime +180 -exec cp {} . \;
tar -cvzf fullcsvs-${arcdate}.tar.gz *.csv
if [ $? -eq 0 ] ; then 
    aws s3 cp fullcsvs-${arcdate}.tar.gz ${BKPBUCKET}/fullcsvs-${arcdate}.tar.gz
    cd ..
    rm -rf tmp 
    logger -s -t $(basename $0 .sh) "purging older raw data"
    echo find ${DATADIR}/orbits/${yr}/fullcsv/processed -mtime +180 -exec rm -f {} \;
    # and last year, because the data is split across dated folders
    lyr=$(date -d 'last year' +%Y)
    echo find ${DATADIR}/orbits/${lyr}/fullcsv/processed -mtime +180 -exec rm -f {} \;
else
    logger -s -t $(basename $0 .sh) "problem creating tarball, not purging older files"
    cd ..
    rm -rf tmp 
fi 

logger -s -t $(basename $0 .sh) "archiving raw station CSVs"
cd $DATADIR/single/rawcsvs
mkdir tmp
cd tmp
find .. -mtime +180 -exec cp {} . \;
tar -cvzf rawcsvs-${arcdate}.tar.gz *.csv
if [ $? -eq 0 ] ; then 
    aws s3 cp rawcsvs-${arcdate}.tar.gz ${BKPBUCKET}/rawcsvs-${arcdate}.tar.gz
    logger -s -t $(basename $0 .sh) "purging older raw data which is now backed up"
    cd ..
    rm -rf tmp 
    echo find ${DATADIR}/single/rawcsvs -mtime +180 -exec rm -f {} \;
else
    logger -s -t $(basename $0 .sh) "problem creating tarball, not purging older files"
    cd ..
    rm -rf tmp 
fi 
