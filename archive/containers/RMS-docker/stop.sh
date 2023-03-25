# script to stop docker container
# Copyright (C) Mark McIntyre

if [ "$1" ==  "" ] ; then
    echo "usage: ./run.sh path/to/rmsdata"
    exit 1
fi
configloc=$1

$contid=(cat ${configloc}/containerid.txt)
docker stop $contid