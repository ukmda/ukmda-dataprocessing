#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cd $here

sudo ls -1 /var/sftp > moved.txt
grep batchs /home/ubuntu/prod/data/reports/stationlogins.txt |awk '{print $3}'| sort > switched.txt
grep ukmonh /home/ubuntu/prod/data/reports/stationlogins.txt |awk '{print $3}'| sort > pending.txt

ssh ukmonhelper2 "~/prod/server_setup/get-nbd.sh" | while read i ; do echo $i | awk -F"/" '{print $4}' ; done > not-being-done.txt
ssh ukmonhelper2 "~/prod/server_setup/get-all.sh" | while read i ; do echo $i | awk -F"/" '{print $4}' ; done > all-accounts.txt

python ~/src/ukmda-dataprocessing/archive/server_setup/checkSftpAccounts.py

echo "Moved:    $(wc -l moved.txt | awk '{print $1}')"
echo "Switched: $(wc -l switched.txt | awk '{print $1}')"
echo "Pending:  $(wc -l pending.txt | awk '{print $1}')"
echo "Total:    $(wc -l still-live.txt | awk '{print $1}')"
echo ""
echo "Not Live: $(wc -l not_live.txt | awk '{print $1}')"
echo "Not Upl:  $(wc -l not_uploading.txt | awk '{print $1}')"
echo ""
echo "Dead:     $(wc -l not-being-done.txt | awk '{print $1}')"
echo ""