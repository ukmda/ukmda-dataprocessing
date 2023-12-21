#!/bin/bash

echo "Setup tests"
ping -c1 www.ukmeteors.co.uk
pip install --upgrade MeteorTools | grep -v 'already satisfied'
pip install pytest pytest-cov | grep -v 'already satisfied'
git clone https://github.com/ukmda/ukmda-dataprocessing.git
cd ./ukmda-dataprocessing/
git checkout $BRANCH
cd ./archive/ukmon_pylib/
curdir=$(pwd -P)
DATADIR=/data
echo DATADIR is $DATADIR curdir is $curdir
export PYTHONPATH=/WesternMeteorPyLib:/RMS:${curdir}
pytest -v ./tests --cov=. --cov-report=term-missing
