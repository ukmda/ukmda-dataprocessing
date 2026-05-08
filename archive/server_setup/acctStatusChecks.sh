#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cd $here

sudo ls -1 /var/sftp  | egrep -v "test|logup" > moved.txt
grep batchs /home/ubuntu/prod/data/reports/stationlogins.txt | cut -c 42-61 | sed 's/ //g' | sort | uniq > switched.txt
grep ukmonh /home/ubuntu/prod/data/reports/stationlogins.txt | cut -c 42-61 | sed 's/ //g' | sort | uniq > pending.txt

ssh ukmonhelper2 "~/prod/server_setup/get-nbd.sh" | while read i ; do echo $i | awk -F"/" '{print $4}' ; done > not-being-done.txt
ssh ukmonhelper2 "~/prod/server_setup/get-all.sh" | while read i ; do echo $i | awk -F"/" '{print $4}' ; done > all-accounts.txt

python ~/src/ukmda-dataprocessing/archive/server_setup/checkSftpAccounts.py


echo "Moved:    $(wc -l moved.txt | awk '{print $1}')" > statusreport.txt
echo "Switched: $(wc -l switched.txt | awk '{print $1}')" >> statusreport.txt
echo "Pending:  $(wc -l pending.txt | awk '{print $1}')" >> statusreport.txt
echo "Total:    $(wc -l still-live.txt | awk '{print $1}')" >> statusreport.txt
echo "" >> statusreport.txt
echo "Not Live: $(wc -l not_live.txt | awk '{print $1}')" >> statusreport.txt
echo "Not Upl:  $(wc -l not_uploading.txt | awk '{print $1}')" >> statusreport.txt
echo "" >> statusreport.txt
echo "Dead:     $(wc -l not-being-done.txt | awk '{print $1}')" >> statusreport.txt
echo "" >> statusreport.txt
cat statusreport.txt