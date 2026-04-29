#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
# create various html and js files of camera info for the website
#
# Parameters
#   none
# 
# Consumes
#   
#
# Produces
#   camera locations file cameraLocs.json
#   camera details file camera-details.csv
#   three html files used by the search page

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration
source $here/../config.ini >/dev/null 2>&1
conda activate ${WMPL_ENV}

logger -s -t updateCameraDets "starting"

python -c "from reports.CameraDetails import updateCamLocDirFovDB; updateCamLocDirFovDB();"
aws s3 cp $DATADIR/admin/cameraLocs.json $UKMONSHAREDBUCKET/admin/ --quiet
aws s3 cp $DATADIR/admin/cameraLocs.json $WEBSITEBUCKET/browse/ --quiet
aws s3 sync $UKMONSHAREDBUCKET/admin/ $DATADIR/admin --quiet

# create the CSV file of camera info and the html versions for search functions on the website

python -c "from reports.CameraDetails import createCDCsv; createCDCsv('consolidated','searchidx');"
aws s3 cp $DATADIR/consolidated/camera-details.csv $UKMONSHAREDBUCKET/consolidated/ --quiet
aws s3 cp $DATADIR/searchidx/statopts.html $WEBSITEBUCKET/search/ --quiet
aws s3 cp $DATADIR/searchidx/activestatopts.html $WEBSITEBUCKET/search/ --quiet
aws s3 cp $DATADIR/searchidx/activestatlocs.html $WEBSITEBUCKET/search/ --quiet

logger -s -t updateCameraDets "finished"
