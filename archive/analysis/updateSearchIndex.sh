#!/bin/bash
#
# script to update match data each night and then recalc any necessary orbits

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1

wait=1
while [ $wait -eq 1 ] ; do 
    if [ ! -f $SRC/data/.nightly_running ] ; then  
        wait=0
    else
        echo "nightly job running, waiting for it to finish"
        sleep 300
    fi
done 

source $WEBSITEKEY
logger -s -t updateSearchIndex "getting latest livefeed CSV files"
yr=$(date +%Y)
mth=$(date +%m)
cq=$(((mth - 1 ) / 3 + 1))
lq=$(((mth - 1 ) / 3 ))
aws s3 cp s3://ukmon-live/idx${yr}0${cq}.csv ${DATADIR}/ukmonlive/
aws s3 cp s3://ukmon-live/idx${yr}0${lq}.csv ${DATADIR}/ukmonlive/

logger -s -t updateSearchIndex "getting list of single jpg files"
aws s3 ls $WEBSITEBUCKET/img/single/$yr/ --recursive | awk '{print $4}' > $DATADIR/singleJpgs.csv

logger -s -t updateSearchIndex "creating searchable indices"
$SRC/analysis/createSearchable.sh

logger -s -t updateSearchIndex "creating station list"
$SRC/website/createStationList.sh

find $SRC/logs -name "updateSearchIndex*" -mtime +7 -exec rm -f {} \;
logger -s -t updateSearchIndex "finished"