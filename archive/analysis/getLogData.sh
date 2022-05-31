#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1
source $HOME/venvs/$WMPL_ENV/bin/activate

if [ "$1" == "" ] ; then
    rundate=$1
else
    rundate=$(date +%Y%m%d)
fi 

lastlog=$(ls -1tr $SRC/logs/nightly*.log | tail -1)
lastmtch=$(ls -1tr $SRC/logs/matches-*.log | tail -1)

egrep "nightlyJob|consolidateOutput|createMthlyExtracts|createShwrExtracts|createSearchable|createFireballPage|showerReport|reportYear|createSummaryTable|createLatestTable|stationReports" $lastlog > /tmp/logmsgs.txt
egrep "findAllMatches1|convertUfoToRms|getRMSSingleData|runMatching" $lastmtch > /tmp/matchpt1.txt
egrep "findAllMatches2|updateIdexPages|createOrbitIndex" $lastmtch > /tmp/matchpt2.txt


cp $TEMPLATES/header.html $DATADIR/lastlog.html
echo "<h2>Batch Job Report</h2>" >> $DATADIR/lastlog.html
echo "<pre>" >> $DATADIR/lastlog.html
head -2 /tmp/logmsgs.txt >> $DATADIR/lastlog.html
cat /tmp/matchpt1.txt >> $DATADIR/lastlog.html
cat /tmp/matchpt2.txt >> $DATADIR/lastlog.html
len=$(wc -l /tmp/logmsgs.txt|awk '{print $1}')
len=$((len-2))
tail -$len /tmp/logmsgs.txt >> $DATADIR/lastlog.html
echo "</pre>" >> $DATADIR/lastlog.html
echo "<h2>Correlator Report</h2>" >> $DATADIR/lastlog.html
echo "<pre>" >> $DATADIR/lastlog.html
python -m reports.getSolutionStati $lastmtch >> $DATADIR/lastlog.html
ls -1 $SRC/logs/distrib/$rundate*.log | while read i ; do
    python -m reports.getSolutionStati $i >> $DATADIR/lastlog.html
done
echo "</pre>" >> $DATADIR/lastlog.html
echo "<h2>Uncalibrated Data Report</h2>" >> $DATADIR/lastlog.html
echo "<pre>" >> $DATADIR/lastlog.html
grep "Skipping" $lastmtch >> $DATADIR/lastlog.html
echo "</pre>" >> $DATADIR/lastlog.html

cat $TEMPLATES/footer.html >> $DATADIR/lastlog.html
rm /tmp/matchpt1.txt /tmp/matchpt2.txt /tmp/logmsgs.txt

source $WEBSITEKEY
aws s3 cp $DATADIR/lastlog.html  $WEBSITEBUCKET/reports/ --quiet
