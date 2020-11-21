#!/bin/bash
source ~/.ssh/ukmon-shared-keys
source ~/venvs/wmpl/bin/activate

if [ $# -eq 0 ]; then
    yr=2020
else
    yr=$1
fi
python ./consolidateAXML.py $yr $2