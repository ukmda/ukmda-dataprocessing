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
for loc in analysis ukmon_pylib website cronjobs utils static_content
do
	rsync -a --delete $loc/ ~/${envname}/$loc
	chmod +x ~/${envname}/$loc/*.sh > /dev/null 2>&1
done
rsync -a share/ ~/${envname}/share

DATADIR=~/$envname/data
mkdir -p $DATADIR/{admin,browse,consolidated,costs,dailyreports,distrib,kmls,manualuploads}
mkdir -p $DATADIR/{lastlogs,latest,matched,orbits,reports,searchidx,single,trajdb,videos}
mkdir -p $DATADIR/browse/{annual,monthly,daily,showers}
mkdir -p ~/$envname/logs

if [ -f ~/.condaon ]
then
    cd $here
    source ~/.condaon
    conda activate wmpl
    pip install -r archive/ukmon_pylib/additional_requirements.txt
fi

# update the IMO and GMN meteor shower tables if missing
if [ ! -f ~/${envname}/share/IMO_Working_Meteor_Shower_List.xml ] 
then
    ~/$envname/cronjobs/getImoWSfile.sh
fi 

read -n 1 -p "Update bashrc and config? (y/N) " yesno 
if [[ "$yesno" == "y"  || "$yesno" == "Y" ]] 
then 
    echo "Updating config for $envname"
    ~/$envname/utils/makeConfig.sh $RUNTIME_ENV
    for fil in .bashrc .bash_aliases .vimrc .condaon 
    do
        rsync -a server_setup/$fil ~
    done 
else
    echo skipping config and bashrc
fi 
echo ""
echo "$msg complete"