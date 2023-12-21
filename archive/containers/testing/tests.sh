#!/bin/bash

echo "Setup tests"
ping -c1 www.ukmeteors.co.uk
pip install --upgrade MeteorTools
pip install pytest pytest-cov
git clone https://github.com/ukmda/ukmda-dataprocessing.git
cd /ukmda-dataprocessing/
git checkout $BRANCH
cd /ukmda-dataprocessing/archive/ukmon_pylib/
export PYTHONPATH=/WesternMeteorPyLib:/RMS://ukmda-dataprocessing/archive/ukmon_pylib
pytest -v ./tests --cov=. --cov-report=term-missing
