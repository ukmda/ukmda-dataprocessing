#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

mkdir -p $DATADIR/manualuploads
cd $DATADIR/manualuploads
aws s3 sync $UKMONSHAREDBUCKET/fireballs/uploads . --exclude "*" --include "*.zip" --exclude "*.done"

newfiles=$(ls -1 *.zip 2> /dev/null)
if [ "$newfiles" != "" ] ; then 
    for fil in $newfiles ; do
        echo processing $fil
        orb=$(basename $fil .zip)
        evt=$(echo ${orb:0:15} | sed 's/-/_/g')
        [ -d $evt ]  && rm -Rf $evt
        mkdir -p $evt/$orb
        cd $evt
        unzip ../$fil
        mv *.pickle $orb
        cd ..
        pick=$(ls -1 $evt/$orb/*.pickle)
        python -m maintenance.recreateOrbitPages $pick force
        ymd=${fil:0:8}
        yr=${ymd:0:4}
        $SRC/website/createOrbitIndex.sh ${ymd}
        aws s3 ls ${UKMONSHAREDBUCKET}/matches/${yr}/fullcsv/
        sleep 30 # to allow the lambda to write the CSV file to s3
        aws s3 ls ${UKMONSHAREDBUCKET}/matches/${yr}/fullcsv/
        $SRC/analysis/consolidateOutput.sh ${yr}
        $SRC/website/createFireballPage.sh ${yr}
        aws s3 mv $UKMONSHAREDBUCKET/fireballs/uploads/$fil $UKMONSHAREDBUCKET/fireballs/uploads/processed/$fil.done
        rm $fil
    done
else
    echo nothing to process
fi