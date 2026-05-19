#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
# script to pull IMO working shower XML file with shower dates and the WMPL static data

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1

logger -s -t getImoWSfile "Getting IMO working shower file"
mkdir -p $DATADIR/share >/dev/null 2>&1
cd $DATADIR/share
mv IMO*.xml $(date +%Y%m%d_%H%M%S).xml > /dev/null 2>&1
/usr/bin/wget https://www.imo.net/members/imo_showers/IMO_Working_Meteor_Shower_list/IMO_Working_Meteor_Shower_List.xml --no-check-certificate
find . -mtime +21 -name "*.xml" -exec rm -f {} \;

# update WMPL static data 
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

pushd $WMPL_LOC
git checkout wmpl/share/streamfulldata.csv
#git checkout wmpl/share/ShowerLookUpTable.txt
git checkout wmpl/share/gmn_shower_table_20230518.txt
rsync wmpl/share/gmn_shower_table_20230518.txt $DATADIR/share/
popd

python -c  "from utils.getActiveShowers import _loadShowerTable;_LoadShowerTable(forceRedo=True)"

logger -s -t getImoWSfile "finished"

