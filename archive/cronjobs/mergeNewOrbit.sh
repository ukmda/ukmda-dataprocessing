#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

mkdir -p $DATADIR/manualuploads
cd $DATADIR/manualuploads
if [ -f ./running ] ; then
   echo "already running"
   exit
fi
touch .running
aws s3 sync $UKMONSHAREDBUCKET/fireballs/uploads . --exclude "*" --include "*.zip" --exclude "*.done"

newfiles=$(ls -1 *.zip 2> /dev/null)
if [ "$newfiles" != "" ] ; then 
    for fil in $newfiles ; do
        echo processing $fil
        ymd=${fil:0:8}
        ym=${fil:0:6}
        yr=${ymd:0:4}
        orb=$(basename $fil .zip)
        evt=$(echo ${orb:0:15} | sed 's/-/_/g')
        [ -d $evt ]  && rm -Rf $evt
        mkdir -p $evt/$orb
        cd $evt
        unzip ../$fil
        mv *.pickle $orb
        cd ..
        pick=$(ls -1 $evt/$orb/*.pickle)
        pickname=$(basename $pick)
        origdir=$(
python << EOD  
from wmpl.Utils.Pickling import loadPickle;
from wmpl.Utils.TrajConversions import jd2Date;
pick = loadPickle('${evt}/$orb','${pickname}');
if hasattr(pick, 'longname'):
    print(pick.longname)
else:
    print(jd2Date(pick.jdt_ref, dt_obj=True).strftime('%Y%m%d_%H%M%S.%f')[:19]+'_UK');
EOD
)
        mv $evt/$orb $evt/$origdir
        aws s3 sync $evt/jpgs s3://ukmda-website/img/single/${yr}/${ym}/
        aws s3 sync $evt/mp4s s3://ukmda-website/img/mp4/${yr}/${ym}/
        aws s3 sync $evt/notes s3://ukmda-website/reports/${yr}/orbits/${ym}/${ymd}/${origdir}/notes
        pick=$(ls -1 $evt/$origdir/*.pickle)
        python -m maintenance.recreateOrbitPages $pick force
        $SRC/website/createOrbitIndex.sh ${ymd}
        sleep 30 # to allow the lambda to write the CSV file to s3
        $SRC/analysis/consolidateOutput.sh ${yr}
        $SRC/website/createFireballPage.sh ${yr}
        aws s3 mv $UKMONSHAREDBUCKET/fireballs/uploads/$fil $UKMONSHAREDBUCKET/fireballs/uploads/processed/$fil.done
        rm $fil
    done
#else
#    echo nothing to process
fi
rm $DATADIR/manualuploads/.running
find $SRC/logs -name "mergeNewOrbit*" -mtime +10 -exec rm -f {} \;
