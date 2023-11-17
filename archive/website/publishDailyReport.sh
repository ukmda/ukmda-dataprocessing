#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre

# Creates the website version of the daily report
#
# Parameters
#   (optional) days back to run for - defaults to yesterday
# 
# Consumes
#   the dailyreport and stats files
#
# Produces
#   a webpage showing the current daily report. 
#   a copy of the report named report_yyyymmdd.txt
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

logger -s -t publishDailyReport "creating report file"
cd $DATADIR

daysback=1
if [ $# -ne 0 ] ; then
    daysback=$1
fi

repdaysback=$((daysback-1))
repdate=$(date --date="$repdaysback days ago" +%Y%m%d)

mkdir -p $DATADIR/latest/dailyreports > /dev/null 2>&1
python -m reports.dailyReport $daysback $DATADIR/dailyreports /tmp

if [ $daysback -ne 1 ] ; then 
    cp $TEMPLATES/header.html $DATADIR/latest/dailyreports/dailyreport_${repdate}.html
    cat /tmp/report_${repdate}.html >> $DATADIR/latest/dailyreports/dailyreport_${repdate}.html 
    cat $TEMPLATES/footer.html >> $DATADIR/latest/dailyreports/dailyreport_${repdate}.html
else 
    cp $TEMPLATES/header.html $DATADIR/latest/dailyreports/dailyreport.html
    cat /tmp/report_latest.html >> $DATADIR/latest/dailyreports/dailyreport.html 
    cat $TEMPLATES/footer.html >> $DATADIR/latest/dailyreports/dailyreport.html
    cp $DATADIR/latest/dailyreports/dailyreport.html $DATADIR/latest/dailyreports/dailyreport_${repdate}.html
fi 
cd $DATADIR/latest/dailyreports
replist=$(ls -1 *.html | grep -v dailyreport.html | grep -v reportsidx.html | sort -r | head -30)

cp $TEMPLATES/header.html $DATADIR/latest/dailyreports/dailyreportsidx.html
echo "<table border=1>" >> $DATADIR/latest/dailyreports/dailyreportsidx.html
for rep in $replist ; do 
    echo "<tr><td><a href=/latest/dailyreports/${rep}>$rep</a></td></tr>" >> $DATADIR/latest/dailyreports/dailyreportsidx.html
done
echo "</table>" >> $DATADIR/latest/dailyreports/dailyreportsidx.html
cat $TEMPLATES/footer.html >> $DATADIR/latest/dailyreports/dailyreportsidx.html

aws s3 sync $DATADIR/latest/dailyreports/  $WEBSITEBUCKET/latest/dailyreports/ --quiet
