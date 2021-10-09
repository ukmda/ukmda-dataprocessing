#!/bin/bash

# bash script to create station list option HTML for the search page

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1

# all cameras
siteidx=$DATADIR/statopts.html

echo "<label for=\"statselect\">Station</label>" > $siteidx
echo "<select class=\"bootstrap-select\" id=\"statselect\">" >> $siteidx
echo "<option value=\"1\" selected=\"selected\">All</option>" >> $siteidx

rowid=2

source ~/venvs/$WMPL_ENV/bin/activate
export PYTHONPATH=$PYLIB:$wmpl_loc
python << EOD >/tmp/camlist.txt
from fileformats import CameraDetails as cd
cinfo=cd.SiteInfo()
ci=cinfo.getAllCamsStr()
print(ci)
EOD
camlist=$(cat /tmp/camlist.txt)
rm -f /tmp/camlist.txt  

for cam in $camlist
do
    echo "<option value=\"${rowid}\">${cam}</option>" >> $siteidx
    rowid=$((rowid+1))
done
echo "</select>" >> $siteidx

source $WEBSITEKEY
aws s3 cp $siteidx $WEBSITEBUCKET/search/ --quiet

# active-only
siteidx=$DATADIR/activestatopts.html

echo "<option value=\"1\" selected=\"selected\">All</option>" > $siteidx

rowid=2

source ~/venvs/$WMPL_ENV/bin/activate
export PYTHONPATH=$PYLIB:$wmpl_loc
python << EOD >/tmp/camlist.txt
from fileformats import CameraDetails as cd
cinfo=cd.SiteInfo()
ci=cinfo.getAllCamsStr(onlyActive=True)
print(ci)
EOD
camlist=$(cat /tmp/camlist.txt)
rm -f /tmp/camlist.txt  

for cam in $camlist
do
    echo "<option value=\"${rowid}\">${cam}</option>" >> $siteidx
    rowid=$((rowid+1))
done
echo "</select>" >> $siteidx

source $WEBSITEKEY
aws s3 cp $siteidx $WEBSITEBUCKET/search/ --quiet

