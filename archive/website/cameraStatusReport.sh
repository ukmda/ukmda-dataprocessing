#!/bin/bash

# create report of camera statuses

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration
source $here/../config/config.ini >/dev/null 2>&1

source ~/venvs/$WMPL_ENV/bin/activate
export PYTHONPATH=$PYLIB
cp $TEMPLATES/header.html /tmp/statrep.html
echo "<h3>Camera status report for the network.</h3> <p>This page provides a status report " >> /tmp/statrep.html
echo "on the feed of daily data from cameras in the network. RMS cameras are reported red if more than three days " >> /tmp/statrep.html
echo "late. UFO cameras are reported red if more than 14 days late." >> /tmp/statrep.html
echo "</p><p>Note that ukmonlive data is not included in this report.</p>" >> /tmp/statrep.html
echo "<div id=\"camrep\" class=\"table-responsive\"></div>" >> /tmp/statrep.html
echo "<script src=\"./camrep.js\"></script>" >> /tmp/statrep.html
cat $TEMPLATES/footer.html >> /tmp/statrep.html

python -m reports.cameraStatusReport $MATCHDIR/RMSCorrelate > /tmp/camrep.js

source $WEBSITEKEY
aws s3 cp /tmp/statrep.html $WEBSITEBUCKET/reports/ --quiet
aws s3 cp /tmp/camrep.js $WEBSITEBUCKET/reports/ --quiet
rm -f /tmp/statrep.html /tmp/camrep.js
