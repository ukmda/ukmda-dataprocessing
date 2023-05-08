#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
# bash script to create station list option HTML for the search page
#
# Parameters
#   none
# 
# Consumes
#   the camera-details file
#
# Produces
#   an html file containing a list of stations as options for the search page
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config.ini >/dev/null 2>&1
source $HOME/venvs/$WMPL_ENV/bin/activate

# all cameras
siteidx=$DATADIR/statopts.html

echo "<label for=\"statselect\">Station</label>" > $siteidx
echo "<select class=\"bootstrap-select\" id=\"statselect\">" >> $siteidx
echo "<option value=\"1\" selected=\"selected\">All</option>" >> $siteidx

python << EOD >/tmp/camlist.txt
from reports import CameraDetails as cd
cinfo=cd.SiteInfo()
ci=cinfo.getAllCamsStr()
print(ci)
EOD
camlist=$(cat /tmp/camlist.txt)
rm -f /tmp/camlist.txt  
rowid=2

for cam in $camlist
do
    echo "<option value=\"${rowid}\">${cam}</option>" >> $siteidx
    rowid=$((rowid+1))
done
echo "</select>" >> $siteidx

aws s3 cp $siteidx $WEBSITEBUCKET/search/ --quiet

# active-only stations
siteidx=$DATADIR/activestatopts.html
echo "<option value=\"1\" selected=\"selected\">All</option>" > $siteidx

python << EOD >/tmp/camlist.txt
from reports import CameraDetails as cd
cinfo=cd.SiteInfo()
ci=cinfo.getAllCamsStr(onlyActive=True)
print(ci)
EOD
camlist=$(cat /tmp/camlist.txt)
rm -f /tmp/camlist.txt  
rowid=2

for cam in $camlist
do
    echo "<option value=\"${rowid}\">${cam}</option>" >> $siteidx
    rowid=$((rowid+1))
done

aws s3 cp $siteidx $WEBSITEBUCKET/search/ --quiet

# active-only locations
siteidx=$DATADIR/activestatlocs.html
echo "<option value=\"1\" selected=\"selected\">All</option>" > $siteidx

python << EOD >/tmp/loclist.txt
from reports import CameraDetails as cd
cinfo=cd.SiteInfo()
ci=cinfo.getAllLocsStr(onlyActive=True)
print(ci)
EOD
camlist=$(cat /tmp/loclist.txt)
rm -f /tmp/loclist.txt  
rowid=2

for cam in $camlist
do
    echo "<option value=\"${rowid}\">${cam}</option>" >> $siteidx
    rowid=$((rowid+1))
done

aws s3 cp $siteidx $WEBSITEBUCKET/search/ --quiet
