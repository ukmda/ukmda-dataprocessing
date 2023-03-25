#!/bin/bash
#  script to login to RMS docker container
# Copyright (C) Mark McIntyre

if [ "$1" ==  "" ] ; then
    echo "usage: ./login.sh path/to/rmsdata"
    exit 1
fi
configloc=$1
contid=$(cat ${configloc}/containerid.txt)
docker exec -it $contid bash