#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
# create page showing last 90 days costs
#
# Parameters
#   none
# 
# Consumes
#   costs data from AWS Cost Explorer
#
# Produces
#   a webpage showing the costs
#       https://archive.ukmeteors.co.uk/reports/costs.html
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration
source $here/../config.ini >/dev/null 2>&1

conda activate $HOME/miniconda3/envs/${WMPL_ENV}
export PYTHONPATH=$PYLIB

logger -s -t costReport "starting"
numdays=90
if [ $# -gt 1 ] ; then numdays = $1 ; fi

mkdir  -p $DATADIR/costs > /dev/null 

export AWS_PROFILE=ukmonshared
logger -s -t costReport "getting data for $numdays for $AWS_PROFILE"
python -m metrics.costMetrics $DATADIR/costs eu-west-2 $numdays
unset AWS_PROFILE

tod=$(date +%d)
if [ "$tod" == "03" ] ; then 
    python -c "from metrics.costMetrics import getAllMthly;getAllMthly();"
fi

cp $DATADIR/costs/costs-*-90-days.jpg $DATADIR/reports

costfile=$DATADIR/reports/costs.html
imgfile3=/reports/costs-183798037734-90-days.jpg

v3=$(cat $DATADIR/costs/costs-183798037734-last.csv)

lastfullcost=$v3

cp $TEMPLATES/header.html $costfile
echo "<h3>Daily running costs</h3>" >> $costfile
echo "<p>This page shows daily running costs by service of the Archive and Calculation Engine " >> $costfile
echo "in USD. <br> " >> $costfile
echo "The last complete day's cost is \$${lastfullcost}" >> $costfile
echo "</p><p>" >> $costfile
echo "<a href=$imgfile3><img src=$imgfile3 width=100%></a><br>" >> $costfile

if [ -f $DATADIR/shwrinfo/costnotes.html ] ; then 
    echo '<p>' >> $costfile
    cat $DATADIR/shwrinfo/costnotes.html >> $costfile
    echo '</p>' >> $costfile
fi 

cat $TEMPLATES/footer.html >> $costfile

finreps=$(aws s3 ls $WEBSITEBUCKET/docs/financial/ | awk '{print $4}')
frjs=$DATADIR/reports/docindex.js
echo "\$(function() { var table = document.createElement(\"table\");" > $frjs
echo "table.className = \"table table-striped table-bordered table-hover table-condensed w-100\";" >> $frjs
echo "table.setAttribute(\"id\", \"fbtableid\");" >> $frjs
for fr in $finreps ; do
    echo "var row = table.insertRow(-1); var cell = row.insertCell(0);" >> $frjs
    echo "cell.innerHTML = \"<a href=/docs/financial/$fr>$fr</a>\";" >> $frjs   
done 
echo "var outer_div = document.getElementById(\"docindex\"); outer_div.appendChild(table); })" >> $frjs

logger -s -t costReport "publishing data"
aws s3 cp $costfile $WEBSITEBUCKET/reports/ --quiet --profile ukmonshared
aws s3 cp $DATADIR/$imgfile3 $WEBSITEBUCKET/reports/ --quiet --profile ukmonshared
aws s3 cp $frjs $WEBSITEBUCKET/docs/ --quiet --profile ukmonshared
logger -s -t costReport "done"
