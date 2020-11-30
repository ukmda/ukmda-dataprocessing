#!/bin/bash

# script to reconsolidate the A.XML files for a whole year

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source ~/.ssh/ukmon-shared-keys
source ~/venvs/wmpl/bin/activate

if [ $# -eq 0 ]; then
    yr=2020
else
    ym=$1
fi

for j in {01,02,03,04,05,06,07,08,09,10,11,12} ;
do
    $here/findAllMatches.sh ${yr}${j}
done
