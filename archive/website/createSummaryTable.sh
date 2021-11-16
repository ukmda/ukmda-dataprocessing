#!/bin/bash

#
# Creates the table and bar chart that appear on the website homepage. 
# Also creates the coverage map, and copies the logfile to the site. 
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1

logger -s -t createSummaryTable "creating summary table"
cd $DATADIR

export PYTHONPATH=$PYLIB:$wmpl_loc
export SRC 
export DATADIR
yr=$(date +%Y)
source ~/venvs/${WMPL_ENV}/bin/activate

python $PYLIB/reports/createSummaryTable.py ./summarytable.js $yr

logger -s -t createSummaryTable "create a coverage map from the kmls"
python $PYLIB/utils/makeCoverageMap.py $CONFIG/config.ini $ARCHDIR/kmls $DATADIR

logger -s -t createSummaryTable "create year-to-date barchart"
pushd $DATADIR
python $PYLIB/reports/createAnnualBarChart.py  $DATADIR/matched/matches-${yr}.csv ${yr}
popd

logger -s -t createSummaryTable "Add last nights log file to the website"
cp $TEMPLATES/header.html $DATADIR/lastlog.html
echo "<pre>" >> $DATADIR/lastlog.html
lastlog=$(ls -1tr $DATADIR/../logs/matches | tail -1)
egrep -v "BOUNDS|WARNING|RuntimeWarning|OptimizeWarning|DeprecationWarning|ABNORMAL|Unsuccessful timing" $DATADIR/../logs/matches/$lastlog >> $DATADIR/lastlog.html
echo "</pre>" >> $DATADIR/lastlog.html
cat $TEMPLATES/footer.html >> $DATADIR/lastlog.html

logger -s -t createSummaryTable "copying to website"
source $WEBSITEKEY
aws s3 cp $DATADIR/summarytable.js  $WEBSITEBUCKET/data/ --quiet
aws s3 cp $DATADIR/coverage.html  $WEBSITEBUCKET/data/ --quiet
aws s3 cp $DATADIR/lastlog.html  $WEBSITEBUCKET/reports/ --quiet
aws s3 cp $DATADIR/Annual-${yr}.jpg $WEBSITEBUCKET/YearToDate.jpg --quiet

logger -s -t createSummaryTable "finished"