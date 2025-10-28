#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

chkrunning=.delrunning
mkdir -p $DATADIR/manualuploads
cd $DATADIR/manualuploads
if [[ -f ./$chkrunning || -f ./running ]] ; then
   echo "update already running"
   exit
fi
touch ./$chkrunning
aws s3 sync $UKMONSHAREDBUCKET/fireballs/uploads . --exclude "*" --include "*.delete" --exclude "*.done"

newfiles=$(ls -1 *.delete 2> /dev/null)
if [ "$newfiles" != "" ] ; then 
    for fil in $newfiles ; do
        orbname=$(cat $fil)
        echo  $(date +%Y-%m-%dT%H:%M:%SZ) removing $orbname
        $SRC/utils/deleteOrbit.sh $orbname
        aws s3 mv $UKMONSHAREDBUCKET/fireballs/uploads/$fil $UKMONSHAREDBUCKET/fireballs/uploads/processed/$fil.done
        rm $fil
    done
fi
rm $DATADIR/manualuploads/$chkrunning
find $SRC/logs -name "deleteDuplicateOrbit*" -mtime +10 -exec rm -f {} \;
