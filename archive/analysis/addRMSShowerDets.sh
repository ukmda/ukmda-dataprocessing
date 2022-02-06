#!/bin/bash

# script to create RMS shower association details for a single day and station, if not already present
# Parameters
#   sitename eg Tackley
#   canname eg UK0006
#   date eg 20210528
#   optional "force" to force recalculation
#
# Consumes: 
#   FTPdetectinfo file for station for required date
#   Caminfo file, to obtain lati and longi of station
#
# Produces:
#   shower maps and assoc files for each source dataset in the original folder
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1
source $HOME/venvs/${RMS_ENV}/bin/activate

if [ $# -lt 3 ] ; then
    echo usage: addRMSShowerDets.sh sitename camname ymd force
    exit
fi
sitename=$1
camname=$2
ymd=$3
force=$4
yy=${ymd:0:4}   
ym=${ymd:0:6}

fpath="$ARCHDIR/$sitename/$camname/$yy/$ym/$ymd"

logger -s -t addRMSShowerDets "starting"
if compgen -G "$fpath/FTPdetect*.txt" > /dev/null ; then 
    ftpfile=$(compgen -G "$fpath/FTPdetect*.txt" | egrep -v "backup|uncal" | head -1) 

    cd $RMS_LOC

    logger -s -t addRMSShowerDets "check if we already processed ${sitename} ${camname}" 
    done=0
    if compgen -G "$fpath/*assoc*.txt"  > /dev/null ; then done=1 ; fi
    if compgen -G "$fpath/nometeors" > /dev/null ; then done=1 ; fi
    if [ "$force" == "force" ] ; then done=0 ; fi
    if [ -z $ftpfile ] ; then done=1 ; fi
    
    if [ $done -eq 0 ] ; then 
        logger -s -t addRMSShowerDets "processing $ymd"
        lati=$(egrep "$sitename" $CAMINFO | grep $camname | awk -F, '{print $10}')
        longi=$(egrep "$sitename" $CAMINFO | grep $camname | awk -F, '{print $9}')

        python -m traj.ufoShowerAssoc "$ftpfile" -y $lati -z $longi

    else
        logger -s -t addRMSShowerDets "skipping $ymd"
    fi
else
    logger -s -t addRMSShowerDets "ftpfile not found in $fpath"
fi
logger -s -t addRMSShowerDets "finished"