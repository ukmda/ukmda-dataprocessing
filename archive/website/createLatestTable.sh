#!/bin/bash
# Creates a report of camera status with images showing latest uploads
# 
# Parameters
#   none
# 
# Consumes
#   stacks and allsky maps from individual cameras, plus the timestamp of upload
#
# Produces
#   a webpage showing the latest stack and map from each camera
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1

logger -s -t createLatestTable "starting"
mkdir ${DATADIR}/latest > /dev/null 2>&1
cd ${DATADIR}/latest

aws s3 ls $WEBSITEBUCKET/latest/ | grep jpg > /tmp/jpglist.txt
python -m reports.createLatestTable /tmp/jpglist.txt $DATADIR/latest
rm -f /tmp/jpglist.txt

logger -s -t createLatestTable "done, sending to website"
aws s3 cp reportindex.js  $WEBSITEBUCKET/latest/ --quiet

logger -s -t createLatestTable "finished"