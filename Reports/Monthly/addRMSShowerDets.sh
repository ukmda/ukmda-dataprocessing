#!/bin/bash

# script to create RMS shower association details if not already present
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
if [[ "$here" == *"prod"* ]] ; then
    source $HOME/prod/config/config.ini >/dev/null 2>&1
else
    source $HOME/src/config/config.ini >/dev/null 2>&1
fi

source /home/ec2-user/venvs/${RMS_ENV}/bin/activate

if [ $# -lt 3 ] ; then
    echo usage: addRMSShowerDets.sh sitename camname ymd
    exit
fi
sitename=$1
camname=$2
ymd=$3
yy=${ymd:0:4}   
ym=${ymd:0:6}

fpath="$ARCHDIR/$sitename/$camname/$yy/$ym/$ymd"

ls -1t $fpath/FTPdetect*.txt > /dev/null 2>&1
if [ $? -ne 0 ] ; then 
    echo ftpfile not found
else
    ftpfile=$(ls -1t $fpath/FTPdetect*.txt | grep -v backup | head -1) > /dev/null 2>&1
    export PYTHONPATH=$RMS_LOC
    cd $RMS_LOC
    ls -1t $fpath/*assoc*.txt >/dev/null 2>&1
    if [ $? -ne 0 ] ; then 
        echo "processing $ymd"
        lati=$(grep $sitename $CAMINFO | grep $camname | awk -F, '{print $10}')
        longi=$(grep $sitename $CAMINFO | grep $camname | awk -F, '{print $9}')

        python $here/ufoShowerAssoc.py $ftpfile -y $lati -z $longi

        assocfile=$(ls -1t $fpath/*assoc*.txt | head -1) > /dev/null 2>&1
        if [ ! -z $assocfile ] ; then 
            mkdir -p ${RCODEDIR}/DATA/consolidated/A > /dev/null 2>&1
            cp $assocfile ${RCODEDIR}/DATA/consolidated/A
        fi
    else
        echo "skipping $ymd"
    fi
fi
