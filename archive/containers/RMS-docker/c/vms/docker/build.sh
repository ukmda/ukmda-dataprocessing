#!/bin/bash
# build the container

# path\to\rmsdata must exist and must contain a folder "config"
# containing the platepar, mask, RMS config file, id_rsa and id_rsa.pub files. 
if [ $# -lt 2 ] ; then
    echo "usage: ./build.sh path/to/rmsdata"
    exit 1
fi
configloc=$1
cp configure_container.sh $configloc/config
docker build . -t rms_ubuntu