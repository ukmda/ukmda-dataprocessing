#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

cd $DATADIR/brightness
rundt=$(date -d "yesterday" +%Y%m%d)
python -m utils.compareBrightnessData $rundt

# leading space to prevent being inserted into environment
pwd=$(aws ssm get-parameters --names prod_dbpw --with-decryption --region eu-west-1 | jq .Parameters[0].Value | sed 's/"//g')
mysql -p$pwd -ubatch -h localhost << EOD
use ukmon;
select count(*) from ukmon.brightness;
load data local infile '${DATADIR}/brightness/CaptureNight_${rundt}.csv' 
into table brightness fields terminated by ',';
select count(*) from ukmon.brightness;
EOD

find ${DATADIR}/brightness -name "CaptureNight*" -mtime +30 -exec rm -f {} \;

