#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

ymd=$1
yr=${ymd:0:4}
ym=${ymd:0:6}
doall=$2

targ=$WEBSITEBUCKET/reports/$yr/orbits/$ym/$ymd
orblist=$(aws s3 ls $targ/ | grep PRE | egrep -v "html|plots|png" | awk '{print $2}')

for orb in $orblist ; do
    srcdir=reports/$yr/orbits/${ym}/$ymd/${orb}
    aws s3 ls $OLDWEBSITEBUCKET/${srcdir}index.html > /dev/null
    if [[ $? -eq 1 || "$doall" == "doall" ]] ; then
        echo $orb
        aws s3 sync $WEBSITEBUCKET/$srcdir $OLDWEBSITEBUCKET/$srcdir --size-only
        pickname=${orb:0:15}_trajectory.pickle
        targdir=matches/RMSCorrelate/trajectories/$yr/$ym/$ymd/$orb
        aws s3 cp $WEBSITEBUCKET/reports/${yr}/orbits/${ym}/${ymd}/${orb}${pickname} $UKMONSHAREDBUCKET/$targdir --profile ukmonshared
        aws s3 cp $WEBSITEBUCKET/reports/${yr}/orbits/${ym}/${ymd}/${orb}${pickname} $OLDUKMONSHAREDBUCKET/$targdir
    fi
done