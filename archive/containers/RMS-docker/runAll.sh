#!/bin/bash
# Copyright (C) Mark McIntyre
# script to run multiple cameras

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $here

rmsdata=/mnt/c/dockervols
camlist="uk001l uk002f"

for cam in $camlist ; do
    ./run.sh $rmsdata/$cam
done 