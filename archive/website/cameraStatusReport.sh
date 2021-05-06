#!/bin/bash

# create report of camera statuses

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration
source $here/../config/config.ini >/dev/null 2>&1

export PYTHONPATH=$PYLIB
cp $TEMPLATES/header.html /tmp/statrep.html
cd $PYLIB
python -m reports.cameraStatusReport $MATCHDIR/RMSCorrelate >> /tmp/statrep.html
cat $TEMPLATES/footer.html >> /tmp/statrep.html

source $WEBSITEKEY
aws s3 cp /tmp/statrep.html $WEBSITEBUCKET/reports/
