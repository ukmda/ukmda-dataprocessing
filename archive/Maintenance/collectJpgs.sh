#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1
source ~/venvs/$WMPL_ENV/bin/activate
source $WEBSITEKEY

cd $SRC/analysis

for yr in 2021 2020 2019 2018 2017 2016 2015 2014 2013 2012 ; do
    for mth in 12 11 10 09 08 07 06 05 04 03 02 01 ; do
        echo $yr $mth
        python initialGetAllJpgs.py $SRC/config/config.ini ${yr}${mth}
        #days=$(aws s3 ls s3://ukmon-shared/archive/Tackley/c1/${yr}/${yr}${mth}/ | grep PRE | awk '{print $2}')
        #for d in $days ; do
        #    echo looking at $d
        #    src=s3://ukmon-shared/archive/Tackley/c1/${yr}/${yr}${mth}/${d}
        #    dest=s3://ukmeteornetworkarchive/img/single/$yr/$yr$mth/
        #    echo $src $dest 
        #    aws s3 cp $src $dest --recursive --exclude "*" --include "*P.jpg" 
        #done
        #aws s3 cp s3://ukmon-shared/archive/Tackley/c1/${yr}/${yr}
    done
done