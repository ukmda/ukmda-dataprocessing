#!/bin/bash

PYTHONPATH=$WMPL_LOC:$RMS_LOC:.:..
export PYTHONPATH

if [ $# == 0 ] ; then
    pytest -v ./tests --cov=. --cov-report=term-missing
else
    pytest -v ./tests/test_$1.py --cov=$1 --cov-report=term-missing
fi
