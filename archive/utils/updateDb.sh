#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

cd $here
if [ $# -lt 1 ] ; then 
	rundt=$(date -d "yesterday" +%Y%m%d)
else
	rundt=$1
fi 

cd ~/prod/data/brightness
mysql -u batch -p$(cat ~/.ssh/db_batch.passwd) -h localhost << EOD
use ukmon;
select count(*) from ukmon.brightness;
load data local infile './CaptureNight_${rundt}.csv' 
into table brightness fields terminated by ',';
select count(*) from ukmon.brightness;
EOD
