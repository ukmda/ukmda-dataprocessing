#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cd $here

sudo ls -1 /var/sftp  | egrep -v "test|logup" > moved.txt
grep batchs /home/ubuntu/prod/data/reports/stationlogins.txt | cut -c 42-61 | sed 's/ //g' | sort | uniq > switched.txt
grep -v batchs /home/ubuntu/prod/data/reports/stationlogins.txt | cut -c 42-61 | sed 's/ //g' | grep -v StationID| sort | uniq > pending.txt

ssh ukmonhelper2 "~/server_setup/get-nbd.sh" | while read i ; do echo $i | awk -F"/" '{print $4}' ; done > dead.txt
ssh ukmonhelper2 "~/server_setup/get-all.sh" | while read i ; do echo $i | awk -F"/" '{print $4}' ; done > all-accounts.txt

python ~/src/ukmda-dataprocessing/archive/server_setup/checkSftpAccounts.py


echo "" > statusreport.txt
echo "Migrated is a count of how many stations got set up on the new server," >> statusreport.txt
echo "Done is how many have cut over, pending is how many have not" >> statusreport.txt
echo "" >> statusreport.txt
echo "Migrated: $(wc -l moved.txt | awk '{print $1}')" >> statusreport.txt
echo "Done:     $(wc -l switched.txt | awk '{print $1}')" >> statusreport.txt
echo "Pending:  $(wc -l pending.txt | awk '{print $1}')" >> statusreport.txt
echo "" >> statusreport.txt
echo "Live is how many have connected in the last 10 days" >> statusreport.txt
echo "Inactive is how many didn't connect for 10 days" >> statusreport.txt
echo "" >> statusreport.txt
echo "Live:     $(cat still-live.txt | sort | uniq | wc -l | awk '{print $1}')" >> statusreport.txt
echo "Not Live: $(cat inactive.txt | sort | uniq | wc -l | awk '{print $1}')" >> statusreport.txt
echo "" >> statusreport.txt
echo "Not Upl is how many aren't uploading" >> statusreport.txt
echo "" >> statusreport.txt
echo "Not Upl:  $(wc -l not_uploading.txt | awk '{print $1}')" >> statusreport.txt
echo "" >> statusreport.txt
echo "Dead is cameras that I'm not intending to migrate either because" >> statusreport.txt
echo "they've left the network or been offline for years" >> statusreport.txt
echo "" >> statusreport.txt
echo "Dead:     $(wc -l dead.txt | awk '{print $1}')" >> statusreport.txt
echo "" >> statusreport.txt
cat statusreport.txt
