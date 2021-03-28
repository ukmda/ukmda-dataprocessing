#!/bin/bash
#
# script to get AWS logs for ukmon data
#
cd ~/prod/logs
source ~/venvs/RMS/bin/activate
source ~/.ssh/ukmonarchive-keys
python ~/src/getlogs/getLogs.py $1
