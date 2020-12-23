#!/bin/bash

# script to create RMS shower association details if not already present
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/config.ini >/dev/null 2>&1
source /home/ec2-user/venvs/RMS/bin/activate

if [ $# -lt 3 ] ; then
    echo usage: addRMSShowerDets.sh sitename camname ymd
    exit
fi
sitename=$1
camname=$2
ymd=$3
yy=${ymd:0:4}
ym=${ymd:0:6}

fpath=$ARCHDIR/$sitename/$camname/$yy/$ym/$ymd
ftpfile=$(ls -1t $fpath/FTPdetect*.txt | grep -v backup | head -1)
assocfile=$(ls -1t $fpath/*assoc*.txt | head -1)

if [ -z $ftpfile ] ; then 
    echo ftpfile not found in $fpath
else
#    if [ ! -z $assocfile ] ; then 
        export PYTHONPATH=$RMS_LOC
        cd $RMS_LOC
        
        lati=$(grep $sitename $CAMINFO | grep $camname | awk -F, '{print $10}')
        longi=$(grep $sitename $CAMINFO | grep $camname | awk -F, '{print $9}')

        python $here/ufoShowerAssoc.py $ftpfile -y $lati -z $longi
#    fi
    assocfile=$(ls -1t $fpath/*assoc*.txt | head -1)
    cp $assocfile /tmp
fi
