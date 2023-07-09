#!/bin/bash

[ -f ~/dev/config.ini ] && source ~/dev/config.ini
[ -f ~/source/testing/config.ini ] && source ~/source/testing/config.ini

if [  "$(which conda)" == "" ] ; then 
    source $HOME/venvs/${WMPL_ENV}/bin/activate
else
    conda activate $HOME/miniconda3/envs/${WMPL_ENV}
fi

export PYTHONPATH=$WMPL_LOC:$RMS_LOC:.:..

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

pip install pytest pytest-cov

cd $here/..
if [ $# == 0 ] ; then
    pytest -v ./tests --cov=. --cov-report=term-missing
else
    pytest -v ./tests/test_$1.py --cov=$1 --cov-report=term-missing
fi
