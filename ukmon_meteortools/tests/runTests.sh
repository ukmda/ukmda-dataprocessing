#!/bin/bash

source ~/dev/config.ini
source ~/venvs/$WMPL_ENV/bin/activate

export PYTHONPATH=$WMPL_LOC:$RMS_LOC:.:..

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

pip install pytest pytest-cov

if [ $# == 0 ] ; then
    pytest -v . --cov=. --cov-report=term-missing
else
    pytest -v ./test_$1.py --cov=$1 --cov-report=term-missing
fi
