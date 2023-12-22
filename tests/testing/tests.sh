#!/bin/bash

echo "Setup tests $1"
ping -c1 www.ukmeteors.co.uk
pip install --upgrade MeteorTools | grep -v 'already satisfied'
pip install pytest pytest-cov | grep -v 'already satisfied'
git clone https://github.com/ukmda/ukmda-dataprocessing.git
cd ./ukmda-dataprocessing/
git checkout $BRANCH
cd ./archive/ukmon_pylib/
curdir=$(pwd -P)
export DATADIR=/data
if [ ! -f $DATADIR/testdata.tar.gz ] ; then 
    echo "collecting test data"
    mkdir /data
    curl https://archive.ukmeteors.co.uk/browse/testdata/testdata.tar.gz  -o /data/testdata.tar.gz
    pushd /data && tar -xzf ./testdata.tar.gz
    curl https://archive.ukmeteors.co.uk/reports/stations/cameraLocs.json -o /data/admin/cameraLocs.json
    popd
fi 
echo DATADIR is $DATADIR curdir is $curdir
export PYTHONPATH=/WesternMeteorPyLib:/RMS:${curdir}
pytest -v ./tests --cov=. --cov-report=term-missing
