#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/config.ini >/dev/null 2>&1

if [ $# -lt 3 ] ; then
    echo usage: updateRMSShowerAssocs.sh sitename camname year
    exit
fi

sitename=$1
camname=$2
yr=$3

ls -1 $ARCHDIR/$sitename/$camname/$yr/${yr}01 | while read i ; do $here/addRMSShowerDets.sh $sitename $camname $i ; done
ls -1 $ARCHDIR/$sitename/$camname/$yr/${yr}02 | while read i ; do $here/addRMSShowerDets.sh $sitename $camname $i ; done
ls -1 $ARCHDIR/$sitename/$camname/$yr/${yr}03 | while read i ; do $here/addRMSShowerDets.sh $sitename $camname $i ; done
ls -1 $ARCHDIR/$sitename/$camname/$yr/${yr}04 | while read i ; do $here/addRMSShowerDets.sh $sitename $camname $i ; done
ls -1 $ARCHDIR/$sitename/$camname/$yr/${yr}05 | while read i ; do $here/addRMSShowerDets.sh $sitename $camname $i ; done
ls -1 $ARCHDIR/$sitename/$camname/$yr/${yr}06 | while read i ; do $here/addRMSShowerDets.sh $sitename $camname $i ; done
ls -1 $ARCHDIR/$sitename/$camname/$yr/${yr}07 | while read i ; do $here/addRMSShowerDets.sh $sitename $camname $i ; done
ls -1 $ARCHDIR/$sitename/$camname/$yr/${yr}08 | while read i ; do $here/addRMSShowerDets.sh $sitename $camname $i ; done
ls -1 $ARCHDIR/$sitename/$camname/$yr/${yr}09 | while read i ; do $here/addRMSShowerDets.sh $sitename $camname $i ; done
ls -1 $ARCHDIR/$sitename/$camname/$yr/${yr}10 | while read i ; do $here/addRMSShowerDets.sh $sitename $camname $i ; done
ls -1 $ARCHDIR/$sitename/$camname/$yr/${yr}11 | while read i ; do $here/addRMSShowerDets.sh $sitename $camname $i ; done
ls -1 $ARCHDIR/$sitename/$camname/$yr/${yr}12 | while read i ; do $here/addRMSShowerDets.sh $sitename $camname $i ; done
