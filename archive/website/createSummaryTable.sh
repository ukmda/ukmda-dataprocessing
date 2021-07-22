#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1

logger -s -t createSummaryTable "creating summary table"
cd $here/../analysis

export PYTHONPATH=$PYLIB:$wmpl_loc
export SRC 
export DATADIR
yr=$(date +%Y)
source ~/venvs/${WMPL_ENV}/bin/activate
python $PYLIB/reports/createSummaryTable.py $here/data/summarytable.js $yr

logger -s -t createSummaryTable "create a coverage map from the kmls"
source ~/venvs/${RMS_ENV}/bin/activate
python $PYLIB/utils/makeCoverageMap.py $CONFIG/config.ini $ARCHDIR/kmls $here/data

logger -s -t createSummaryTable "create year-to-date barchart"
pushd $DATADIR
python $PYLIB/reports/createAnnualBarChart.py  $DATADIR/UKMON-all-matches.csv
popd

logger -s -t createSummaryTable "Add last nights log file to the website"
cp $TEMPLATES/header.html /tmp/lastlog.html
echo "<pre>" >> /tmp/lastlog.html
lastlog=$(ls -1tr $SRC/logs/matches | tail -1)
cat $SRC/logs/matches/$lastlog >> /tmp/lastlog.html
echo "</pre>" >> /tmp/lastlog.html
cat $TEMPLATES/footer.html >> /tmp/lastlog.html

logger -s -t createSummaryTable "copying to website"
source $WEBSITEKEY
aws s3 cp $here/data/summarytable.js  $WEBSITEBUCKET/data/ --quiet
aws s3 cp $here/data/coverage.html  $WEBSITEBUCKET/data/ --quiet
aws s3 cp /tmp/lastlog.html  $WEBSITEBUCKET/reports/ --quiet
aws s3 cp $DATADIR/YearToDate.png $WEBSITEBUCKET/ --quiet

logger -s -t createSummaryTable "finished"