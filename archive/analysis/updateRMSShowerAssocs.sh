#!/bin/bash

#
# Examines new RMS data and generates a shower association map if its missing
#
# Parameters
#   year and month in yyyymm format OR days back to scan
#    (optional) "force" to make the reprocessing happen even if already done
#
# Consumes
#   All single-station archive data in $ARCHDIR
#
# Produces
#   new shower association data in $ARCHDIR

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

if [ $# -lt 1 ] ; then
    echo usage: updateRMSShowerAssocs.sh yearmth_or_daysback force
    exit
fi
if [ $1 -lt 2000 ] ; then
    daysback=$1
else 
    ym=$1
    yr=${ym:0:4}   
    mth=${ym:4:6}
fi
force=$2

logger -s -t updateRMSShowerAssocs "starting"

cat $CAMINFO | while read li ; do 
    typ=$(echo $li | awk -F, '{printf("%s", $12)}') 

    if [ "${li:0:1}" != "#" ] ; then
        if [ ${typ:0:1} -eq 2 ] ; then 
            sitename=$(echo $li | awk -F, '{printf("%s", $1)}')
            camname=$(echo $li | awk -F, '{printf("%s", $2)}')

            if [ "$mth" == "" ] ; then
                # parameter was days-back to scan
                for i in $(seq 1 $daysback); do 
                    targdt=$(date --date="$i day ago" +%Y%m%d)
                    yr=${targdt:0:4}   
                    ym=${targdt:0:6}
                    pth="$ARCHDIR/$sitename/$camname/$yr/${ym}/${targdt}"
                    $here/addRMSShowerDets.sh "$sitename" $camname $targdt $force
                done 
            else
                # given a specific month to scan
                if compgen -G ""$ARCHDIR/$sitename/$camname/$yr/${yr}${mth}"/*" > /dev/null ; then 
                    ls -1 "$ARCHDIR/$sitename/$camname/$yr/${yr}${mth}" | while read i
                    do 
                        $here/addRMSShowerDets.sh "$sitename" $camname "$i" $force
                    done
                fi
            fi
        fi 
    fi
done
logger -s -t updateRMSShowerAssocs "finished"

