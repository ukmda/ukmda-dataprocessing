#!/bin/bash

source ~/dev/config.ini
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

export PYTHONPATH=$WMPL_LOC:$RMS_LOC:.:..

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

pip install pytest pytest-cov

cd $here
curl https://archive.ukmeteors.co.uk/browse/testdata/testdata.tar.gz .
tar -xvf ./testdata.tar.gz ./data/
mkdir ~/.aws
cp ./data/profile/credentials ~/.aws/

cd $here/..
if [ $# == 0 ] ; then
    pytest -v ./tests --cov=. --cov-report=term-missing
    pytest -v ../samfunctions/liveDetectionsReport/detectionsCsv.py
else
    pytest -v ./tests/test_$1.py --cov=$1 --cov-report=term-missing
fi

