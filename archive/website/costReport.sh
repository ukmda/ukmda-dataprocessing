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

logger -s -t costReport "starting"
numdays=90
if [ $# -gt 1 ] ; then numdays = $1 ; fi

mkdir  -p $DATADIR/costs > /dev/null 

#export AWS_PROFILE=Mark
#python -m metrics.costMetrics $DATADIR/costs eu-west-2 $numdays

export AWS_PROFILE=realukms
python -m metrics.costMetrics $DATADIR/costs eu-west-2 $numdays
unset AWS_PROFILE

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
#imgfile=/reports/costs-317976261112-90-days.jpg
#imgfile2=/reports/costs-822069317839-90-days.jpg
imgfile3=/reports/costs-183798037734-90-days.jpg

#v1=$(cat $DATADIR/costs/costs-317976261112-last.csv)
#v2=$(cat $DATADIR/costs/costs-822069317839-last.csv)
v3=$(cat $DATADIR/costs/costs-183798037734-last.csv)

#lastfullcost=$(echo $v1 + $v2 + $v3 | bc)
lastfullcost=$v3

cp $TEMPLATES/header.html $costfile
echo "<h3>Daily running costs</h3>" >> $costfile
echo "<p>This page shows daily running costs by service of the Archive and Calculation Engine " >> $costfile
echo "in USD. Until August 2023, costs were split across two accounts for historical reasons. " >> $costfile
echo "The system has now been consolidated into a single account, simplifying reporting. " >> $costfile
echo "AWS cost data may lag by up to a day, so yesterday's costs data are incomplete. The " >> $costfile
echo "last complete day's cost is \$${lastfullcost}" >> $costfile
echo "</p><p>" >> $costfile
#echo "<a href=$imgfile><img src=$imgfile width=100%></a><br>" >> $costfile
#echo "<a href=$imgfile2><img src=$imgfile2 width=100%></a><br>" >> $costfile
echo "<a href=$imgfile3><img src=$imgfile3 width=100%></a><br>" >> $costfile

if [ -f $DATADIR/shwrinfo/costnotes.html ] ; then 
    echo '<p>' >> $costfile
    cat $DATADIR/shwrinfo/costnotes.html >> $costfile
    echo '</p>' >> $costfile
fi 

cat $TEMPLATES/footer.html >> $costfile

logger -s -t costReport "publishing data"
aws s3 cp $costfile $WEBSITEBUCKET/reports/ --quiet
#aws s3 cp $DATADIR/$imgfile $WEBSITEBUCKET/reports/ --quiet 
#aws s3 cp $DATADIR/$imgfile2 $WEBSITEBUCKET/reports/ --quiet
aws s3 cp $DATADIR/$imgfile3 $WEBSITEBUCKET/reports/ --quiet

aws s3 cp $costfile $OLDWEBSITEBUCKET/reports/ --quiet
aws s3 cp $DATADIR/$imgfile $OLDWEBSITEBUCKET/reports/ --quiet 
#aws s3 cp $DATADIR/$imgfile2 $OLDWEBSITEBUCKET/reports/ --quiet
#aws s3 cp $DATADIR/$imgfile3 $OLDWEBSITEBUCKET/reports/ --quiet

logger -s -t costReport "done"
