#!/bin/bash

echo "Setup tests"
ping -c1 www.ukmeteors.co.uk
pip install --upgrade MeteorTools | grep -v 'already satisfied'
pip install pytest pytest-cov grep -v 'already satisfied'
git clone https://github.com/ukmda/ukmda-dataprocessing.git
cd ./ukmda-dataprocessing/
git checkout $BRANCH
cd ./ukmon_pylib/
curdir=$(pwd -P)
export PYTHONPATH=/WesternMeteorPyLib:/RMS:${curdir}
pytest -v ./tests --cov=. --cov-report=term-missing
