#!/bin/bash

echo "Setup tests"
ping -c1 www.ukmeteors.co.uk
pip install --upgrade MeteorTools
pip install pytest pytest-cov
cd /tmp
git clone https://github.com/ukmda/ukmda-dataprocessing.git
cd /tmp/ukmda-dataprocessing/archive/ukmon_pylib/
export PYTHONPATH=/WesternMeteorPyLib:/RMS:/tmp/ukmda-dataprocessing/archive/ukmon_pylib
pytest -v ./tests --cov=. --cov-report=term-missing
