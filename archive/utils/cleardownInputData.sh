#!/bin/bash

# cleardown of the RMSCorrelate/UK* folders
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
source $HOME/venvs/$WMPL_ENV/bin/activate

currmth=$(date +%Y%m)
if [ $# -lt 1 ] ; then echo "Please supply a month to run for in YYYYMM format"; exit 1 ; fi
ym=$1
if [ $((currmth-ym)) -lt 2 ] ; then echo "cant clear down current or last month" ; exit 1 ; fi 

echo "Getting list of files for ${ym}"
find $MATCHDIR/RMSCorrelate -maxdepth 2 -name "UK????_${ym}*"  -type d -exec ls -1d {} \; > /tmp/cleardown${ym}.txt


if [ -f $DATADIR/olddata/rawdata-${ym}.tar.gz ] ; then 
    echo "Adding to compressed archive rawdata-${ym}.tar.gz"
    gunzip $DATADIR/olddata/rawdata-${ym}.tar.gz
    tar uvf $DATADIR/olddata/rawdata-${ym}.tar -T /tmp/cleardown${ym}.txt
    gzip $DATADIR/olddata/rawdata-${ym}.tar
else 
    echo "Creating compressed archive rawdata-${ym}.tar.gz"
    tar cvfz $DATADIR/olddata/rawdata-${ym}.tar.gz -T /tmp/cleardown${ym}.txt
fi 

if [ $? -ne 0 ] ; then 
    echo "error creating tarfile"
else 
    echo "deleting backed up files"
    cat /tmp/cleardown${ym}.txt | while read fname ; do
        rm -Rv $fname
    done
    echo "now rm /tmp/cleardown${ym}.txt"
fi
echo done