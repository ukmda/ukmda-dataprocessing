#!/bin/bash
#
# script to get AWS logs for ukmon data
#
cd ~/src/ukmon-shared/logs
source ~/venvs/ukmon/bin/activate
source ../getlogs/.ukmoncreds
python ../getlogs/getLogs.py $1
