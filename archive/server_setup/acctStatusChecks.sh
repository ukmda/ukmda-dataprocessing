#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cd $here

sudo ls -1 /var/sftp > done.txt
grep ukmonh /home/ubuntu/prod/data/reports/stationlogins.txt |awk '{print $3}'| sort > pending.txt

ssh ukmonhelper2 "~/prod/server_setup/get-nbd.sh" | while read i ; do echo $i | awk -F"/" '{print $4}' ; done > not-being-done.txt
ssh ukmonhelper2 "~/prod/server_setup/get-all.sh" | while read i ; do echo $i | awk -F"/" '{print $4}' ; done > all-accounts.txt

python ~/src/ukmda-dataprocessing/archive/server_setup/checkSftpAccounts.py
