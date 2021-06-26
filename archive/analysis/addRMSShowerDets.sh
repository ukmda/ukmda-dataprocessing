#!/bin/bash

# script to create RMS shower association details if not already present
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

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

logger -s -t addRMSShowerDets "starting"
if compgen -G "$fpath/FTPdetect*.txt" > /dev/null ; then 
    ftpfile=$(compgen -G "$fpath/FTPdetect*.txt" | grep -v backup | head -1) 

    export PYTHONPATH=$RMS_LOC:$PYLIB
    cd $RMS_LOC

    logger -s -t addRMSShowerDets "check if we already processed ${sitename} ${camname}" 
    done=0
    if compgen -G "$fpath/*assoc*.txt"  > /dev/null ; then done=1 ; fi
    if compgen -G "$fpath/nometeors" > /dev/null ; then done=1 ; fi
    
    if [ $done -eq 0 ] ; then 
        logger -s -t addRMSShowerDets "processing $ymd"
        lati=$(egrep "$sitename" $CAMINFO | grep $camname | awk -F, '{print $10}')
        longi=$(egrep "$sitename" $CAMINFO | grep $camname | awk -F, '{print $9}')

        python $PYLIB/traj/ufoShowerAssoc.py "$ftpfile" -y $lati -z $longi

        if [ $? -eq 0 ] ; then 
            if compgen -G "$fpath/*assoc*.txt"  > /dev/null ; then 
                mkdir -p ${DATADIR}/consolidated/A > /dev/null 2>&1
                assocfile=$(compgen -G "$fpath/*assoc*.txt")
                cp "$assocfile" ${DATADIR}/consolidated/A
            fi
        fi
    else
        logger -s -t addRMSShowerDets "skipping $ymd"
    fi
else
    logger -s -t addRMSShowerDets "ftpfile not found in $fpath"
fi
logger -s -t addRMSShowerDets "finished"