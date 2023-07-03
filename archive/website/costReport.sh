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
#       https://archive.ukmeteornetwork.co.uk/reports/costs.html
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration
source $here/../config.ini >/dev/null 2>&1

conda activate $HOME/miniconda3/envs/${WMPL_ENV}
export PYTHONPATH=$PYLIB

numdays=90
if [ $# -gt 1 ] ; then numdays = $1 ; fi

export AWS_PROFILE=Mark
python -m metrics.costMetrics $SRC/costs eu-west-2 $numdays

export AWS_PROFILE=ukmonshared
python -m metrics.costMetrics $SRC/costs eu-west-2 $numdays

unset AWS_PROFILE

cp $SRC/costs/costs-*-90-days.jpg $DATADIR/reports

costfile=$DATADIR/reports/costs.html
imgfile=/reports/costs-317976261112-90-days.jpg
imgfile2=/reports/costs-822069317839-90-days.jpg

v1=$(cat $SRC/costs/costs-317976261112-last.csv)
v2=$(cat $SRC/costs/costs-822069317839-last.csv)

lastfullcost=$(echo $v1 + $v2 | bc)

cp $TEMPLATES/header.html $costfile
echo "<h3>Daily running costs</h3>" >> $costfile
echo "<p>This page shows daily running costs by service of the Archive and Calculation Engine " >> $costfile
echo "in USD and excluding VAT. Costs are split across two accounts for historical reasons. " >> $costfile
echo "AWS cost data may lag by up to a day, so yesterday's costs data are incomplete. The " >> $costfile
echo "last complete day's cost is \$${lastfullcost}" >> $costfile
echo "</p><p>" >> $costfile
echo "<a href=$imgfile><img src=$imgfile width=100%></a><br>" >> $costfile
echo "<a href=$imgfile2><img src=$imgfile2 width=100%></a><br>" >> $costfile

if [ -f $DATADIR/shwrinfo/costnotes.html ] ; then 
    echo '<p>' >> $costfile
    cat $DATADIR/shwrinfo/costnotes.html >> $costfile
    echo '</p>' >> $costfile
fi 

cat $TEMPLATES/footer.html >> $costfile

aws s3 cp $costfile $WEBSITEBUCKET/reports/ --quiet
aws s3 cp $DATADIR/$imgfile $WEBSITEBUCKET/reports/ --quiet 
aws s3 cp $DATADIR/$imgfile2 $WEBSITEBUCKET/reports/ --quiet
