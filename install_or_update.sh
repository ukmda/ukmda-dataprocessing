#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre

if [[ "$1" != "PROD" && "$1" != "DEV" ]] ; then
    echo "must provide runtime env of PROD or DEV"
    exit -1
fi 
RUNTIME_ENV=$1
envname=$(echo $RUNTIME_ENV | tr '[:upper:]' '[:lower:]')

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

mkdir -p ~/${envname}

cd $here/archive
git pull

[ -d ~/$envname/data ] && msg="upgrade" || msg="install"
for loc in analysis ukmon_pylib website cronjobs utils share static_content
do
	rsync -avz --delete $loc/ ~/${envname}/$loc
	chmod +x ~/${envname}/$loc/*.sh > /dev/null 2>&1
done
DATADIR=~/$envname/data
mkdir -p $DATADIR/{admin,browse,consolidated,costs,dailyreports,distrib,kmls,manualuploads}
mkdir -p $DATADIR/{lastlogs,latest,matched,orbits,reports,searchidx,single,trajdb,videos}
mkdir -p $DATADIR/browse/{annual,monthly,daily,showers}
mkdir -p ~/$envname/logs

echo "$msg complete"