#!/bin/bash
# script to pull IMO working shower XML file with shower dates and the WMPL static data

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

logger -s -t getImoWSfile "Getting IMO working shower file"
mkdir -p $SRC/share >/dev/null 2>&1
cd $SRC/share
mv IMO*.xml $(date +%Y%m%d_%H%M%S).xml
/usr/bin/wget https://www.imo.net/members/imo_showers/IMO_Working_Meteor_Shower_list/IMO_Working_Meteor_Shower_List.xml --no-check-certificate

# update WMPL static data 
source ~/venvs/$WMPL_ENV/bin/activate
export PYTHONPATH=$PYLIB:$wmpl_loc
export wmpl_loc

cd $wmpl_loc
git checkout wmpl/share/streamfulldata.csv
git checkout wmpl/share/ShowerLookUpTable.txt
python -m utils.getShowerDates refresh

logger -s -t getImoWSfile "finished"

