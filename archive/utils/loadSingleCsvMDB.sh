#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1

yr=$1
if [ "$yr" == "" ] ; then
    yr=$(date +%Y)
fi 

cd ${DATADIR}

csvname=$DATADIR/single/singles-${yr}.csv
if [ ! -f $csvname ] ; then echo "$csvname not found" ; exit ; fi
echo "loading $csvname into mariadb"
logger -s -t loadSQL "starting"
user=batch
# leading space to prevent being inserted into environment
passwd=$(aws ssm get-parameters --names prod_dbpw --with-decryption --region eu-west-1 | jq .Parameters[0].Value | sed 's/"//g')
mysql -p${passwd} -u${user} << EOD
select count(*) from ukmon.singles;
LOAD DATA LOCAL INFILE '$csvname' 
INTO TABLE ukmon.singles
FIELDS TERMINATED BY ',' 
ENCLOSED BY '\"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;
select count(*) from ukmon.singles;
EOD

logger -s -t loadSQL "done"
