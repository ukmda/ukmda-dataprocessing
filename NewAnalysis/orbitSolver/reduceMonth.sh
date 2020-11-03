#!/bin/bash
# bash script to reduce a month of data
#

source ./orbitsolver.ini > /dev/null 2>&1

ls -1d ~/ukmon-shared/matches/$1*  | while read i
do
    ./reduceOrbit.sh $i
done

