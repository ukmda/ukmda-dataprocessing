#!/bin/bash
# script to pull IMO working shower XML file with shower dates in

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

mkdir -p $SRC/share >/dev/null 2>&1
cd $SRC/share
mv IMO*.xml $(date +%Y%m%d_%H%M%S).xml
/usr/bin/wget https://www.imo.net/members/imo_showers/IMO_Working_Meteor_Shower_list/IMO_Working_Meteor_Shower_List.xml --no-check-certificate
