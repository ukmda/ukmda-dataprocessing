#!/bin/bash

[ -f ~/dev/config.ini ] && source ~/dev/config.ini
[ -f ~/source/testing/config.ini ] && source ~/source/testing/config.ini

export PYTHONPATH=$WMPL_LOC:$RMS_LOC:.:..
echo running on $(hostname)
pip install requests pandas 

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
pip install pytest pytest-cov 
cd $here

pytest -v --cov=. --cov-report=term-missing  ./test_apis.py