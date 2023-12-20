#!/bin/bash

echo "Setup tests"
ping -c1 www.ukmeteors.co.uk
pip install --upgrade MeteorTools
export PYTHONPATH=/WesternMeteorPyLib:/RMS
curl "https://archive.ukmeteors.co.uk/tmp/remotetest.py" -o /tmp/remotetest.py
python /tmp/remotetest.py
