#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $here

rmsdata=/mnt/c/dockervols
camlist="uk001l uk002f"

for cam in $camlist ; do
    echo ./run.sh $rmsdata/$cam
done 