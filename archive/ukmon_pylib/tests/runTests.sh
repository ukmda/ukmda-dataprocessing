#!/bin/bash

source ~/dev/config.ini
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

export PYTHONPATH=$WMPL_LOC:$RMS_LOC:.:..

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

pip install pytest pytest-cov

cd $here/..
if [ $# == 0 ] ; then
    pytest -v ./tests --cov=. --cov-report=term-missing
    pytest -v ../samfunctions/liveDetectionsReport/detectionsCsv.py
else
    pytest -v ./tests/test_$1.py --cov=$1 --cov-report=term-missing
fi

