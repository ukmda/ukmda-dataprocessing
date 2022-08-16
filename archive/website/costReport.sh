#!/bin/bash
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

source ~/venvs/$WMPL_ENV/bin/activate
export PYTHONPATH=$PYLIB

numdays=90
if [ $# -gt 1 ] ; then numdays = $1 ; fi

export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id --profile Mark)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key --profile Mark)
python -m metrics.costMetrics $SRC/costs eu-west-2 $numdays

export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id --profile ukmonarchive)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key --profile ukmonarchive)
python -m metrics.costMetrics $SRC/costs eu-west-2 $numdays

export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=

cp $SRC/costs/costs-*-90-days.jpg $DATADIR/reports

costfile=$DATADIR/reports/costs.html
imgfile=/reports/costs-317976261112-90-days.jpg
imgfile2=/reports/costs-822069317839-90-days.jpg

cp $TEMPLATES/header.html $costfile
echo "<h3>Daily running costs</h3>" >> $costfile
echo "<p>This page shows daily running costs by service of the Archive and Calculation Engine, in USD " >> $costfile
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
