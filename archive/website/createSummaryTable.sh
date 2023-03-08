#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
# Creates the table and bar chart that appear on the website homepage. 
# Also creates the coverage map, and copies the logfile to the site. 
#
# Parameters
#   none
# 
# Consumes
#   the single station and matched station data files in $DATADIR/single and $DATADIR/matched
#   the most recent match run logfile
#
# Produces
#   a webpage showing the current summary  - the site homepage
#   the annual barchart of matches
#   a copy of the matching run logfile
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config.ini >/dev/null 2>&1
source $HOME/venvs/${WMPL_ENV}/bin/activate
$SRC/utils/clearCaches.sh

logger -s -t createSummaryTable "starting"
cd $DATADIR

yr=$(date +%Y)

python -m reports.createSummaryTable $yr

logger -s -t createSummaryTable "create a coverage map from the kmls"
# make sure correct version of GEOS and PROJ4 available for mapping routines

LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/geos/lib:/usr/local/proj4/lib
export LD_LIBRARY_PATH
mkdir -p $DATADIR/kmls
aws s3 sync $WEBSITEBUCKET/img/kmls/ $DATADIR/kmls --quiet --profile ukmonshared
export KMLTEMPLATE="*25km.kml"
python -m utils.makeCoverageMap $DATADIR/kmls $DATADIR
export KMLTEMPLATE="*70km.kml"
python -m utils.makeCoverageMap $DATADIR/kmls $DATADIR
export KMLTEMPLATE="*100km.kml"
python -m utils.makeCoverageMap $DATADIR/kmls $DATADIR

python -c "from utils.makeCoverageMap import createCoveragePage as ccp ; ccp() ;"

logger -s -t createSummaryTable "create year-to-date barchart"
pushd $DATADIR
python -m reports.createAnnualBarChart  $DATADIR/matched/matches-full-${yr}.parquet.snap ${yr}
popd

# update index page
numcams=$(python -c "from fileformats import CameraDetails as cd; print(len(cd.SiteInfo().getActiveCameras()))")
cat $TEMPLATES/frontpage.html | sed "s/#NUMCAMS#/$numcams/g" > $DATADIR/newindex.html

logger -s -t createSummaryTable "copying to website"
aws s3 cp $DATADIR/latest/coverage-maps.html $WEBSITEBUCKET/latest/ --quiet
aws s3 cp $DATADIR/summarytable.js  $WEBSITEBUCKET/data/ --quiet
aws s3 cp $DATADIR/coverage-100km.html  $WEBSITEBUCKET/data/ --quiet
aws s3 cp $DATADIR/coverage-70km.html  $WEBSITEBUCKET/data/ --quiet
aws s3 cp $DATADIR/coverage-70km.html  $WEBSITEBUCKET/data/coverage.html --quiet
aws s3 cp $DATADIR/coverage-25km.html  $WEBSITEBUCKET/data/ --quiet
aws s3 cp $DATADIR/Annual-${yr}.jpg $WEBSITEBUCKET/YearToDate.jpg --quiet
aws s3 cp $DATADIR/newindex.html $WEBSITEBUCKET/index.html --quiet
aws s3 cp $SRC/website/templates/header.html $WEBSITEBUCKET/templates/ --quiet
aws s3 cp $SRC/website/templates/footer.html $WEBSITEBUCKET/templates/ --quiet

$SRC/utils/clearCaches.sh
logger -s -t createSummaryTable "finished"