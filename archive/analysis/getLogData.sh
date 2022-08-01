#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
source $HOME/venvs/$WMPL_ENV/bin/activate

if [ "$1" != "" ] ; then
    rundate=$1
else
    rundate=$(date +%Y%m%d)
fi 

lastlog=$(ls -1tr $SRC/logs/nightly*.log | tail -1)
lastmtch=$(ls -1tr $SRC/logs/matches-*.log | tail -1)

egrep "nightlyJob|consolidateOutput|createMthlyExtracts|createShwrExtracts|createSearchable|createFireballPage|showerReport|reportYear|createSummaryTable|createLatestTable|stationReports" $lastlog > /tmp/logmsgs.txt
egrep "findAllMatches1|convertUfoToRms|getRMSSingleData|runDistrib" $lastmtch > /tmp/matchpt1.txt
egrep "findAllMatches2|updateIdexPages|createOrbitIndex" $lastmtch > /tmp/matchpt2.txt

python -m reports.findFailedMatches $rundate

cp $TEMPLATES/header.html $DATADIR/lastlog.html
echo "<p>" >> $DATADIR/lastlog.html
echo "Jump to:<p>" >> $DATADIR/lastlog.html >> $DATADIR/lastlog.html
echo "<li><a href=#correl>Correlation Results</a></li>" >> $DATADIR/lastlog.html
echo "<li><a href=#uncal>Uncalibrated Data</a></li>" >> $DATADIR/lastlog.html
echo "<li><a href=#fails>Match Fails</a></li>" >> $DATADIR/lastlog.html
echo "<li><a href=/reports/lastlogs/index.html>Previous Logs</a></li>" >> $DATADIR/lastlog.html
echo "</p>" >> $DATADIR/lastlog.html

echo "<h2 id=batch>Batch Job Report</h2>" >> $DATADIR/lastlog.html
echo "<p>This section shows the output of the daily batch.</p>">> $DATADIR/lastlog.html
echo "<pre>" >> $DATADIR/lastlog.html
head -2 /tmp/logmsgs.txt >> $DATADIR/lastlog.html
cat /tmp/matchpt1.txt >> $DATADIR/lastlog.html
cat /tmp/matchpt2.txt >> $DATADIR/lastlog.html
len=$(wc -l /tmp/logmsgs.txt|awk '{print $1}')
len=$((len-2))
tail -$len /tmp/logmsgs.txt >> $DATADIR/lastlog.html
echo "</pre>" >> $DATADIR/lastlog.html

echo "<h2 id=correl>Correlator Report</h2>" >> $DATADIR/lastlog.html
echo "<p>This section shows the output of the trajectory solver. ">> $DATADIR/lastlog.html
echo "The first part lists any previous solutions for which potential new data were ">> $DATADIR/lastlog.html
echo "available. Subsequent sections show the results of new solutions.</p>">> $DATADIR/lastlog.html
echo "<pre>" >> $DATADIR/lastlog.html
python -m reports.getSolutionStati $lastmtch >> $DATADIR/lastlog.html
ls -1 $SRC/logs/distrib/$rundate*.log | while read i ; do
    python -m reports.getSolutionStati $i >> $DATADIR/lastlog.html
done
echo "</pre>" >> $DATADIR/lastlog.html

echo "<h2 id=uncal>Uncalibrated Data Report</h2>" >> $DATADIR/lastlog.html
echo "<p>This section shows detections that were not included in the correlation run, ">> $DATADIR/lastlog.html
echo "either because RMS was not able to recalibrate the detection or because ">> $DATADIR/lastlog.html
echo "the entire night was uncalibrated (indicated by the 'skipping' warning).</p>">> $DATADIR/lastlog.html
echo "<p>To interpret these data, see " >> $DATADIR/lastlog.html
echo "<a href=https://github.com/markmac99/ukmon-pitools/wiki/UKMON-Pi-Toolset-FAQ#Interpreting_the_Uncalibrated_Report>here<a></p>" >> $DATADIR/lastlog.html
echo "<pre>" >> $DATADIR/lastlog.html
grep "Skipping" $lastmtch >> $DATADIR/lastlog.html
echo "</pre>" >> $DATADIR/lastlog.html

echo "<h2 id=fails>Failed Match Report</h2>" >> $DATADIR/lastlog.html
echo "<p>This section shows groups of potential matches that could not be solved. ">> $DATADIR/lastlog.html
echo "<p>To interpret these data, see " >> $DATADIR/lastlog.html
echo "<pre>" >> $DATADIR/lastlog.html
echo "<a href=https://github.com/markmac99/ukmon-pitools/wiki/Trajectory-Solver-Failureshere<a></p>" >> $DATADIR/lastlog.html
cat $DATADIR/failed/${rundate}_failed.txt >> $DATADIR/lastlog.html
echo "</pre>" >> $DATADIR/lastlog.html

cat $TEMPLATES/footer.html >> $DATADIR/lastlog.html
rm /tmp/matchpt1.txt /tmp/matchpt2.txt /tmp/logmsgs.txt

aws s3 cp $DATADIR/lastlog.html  $WEBSITEBUCKET/reports/ --quiet
aws s3 cp $DATADIR/lastlog.html  $WEBSITEBUCKET/reports/lastlogs/lastlog-${rundate}.html --quiet

if [ ! -d $DATADIR/lastlogs ] ; then mkdir $DATADIR/lastlogs ; fi
cp $DATADIR/lastlog.html $DATADIR/lastlogs/lastlog-${rundate}.html
cp $TEMPLATES/header.html $DATADIR/lastlogs/index.html
ls -1r $DATADIR/lastlogs/last*.html  | head -90 | while read i ; do
    bn=$(basename $i)
    echo "<a href=/reports/lastlogs/$bn>$bn</a><br>" >> $DATADIR/lastlogs/index.html
done
cat $TEMPLATES/footer.html >> $DATADIR/lastlogs/index.html
aws s3 cp $DATADIR/lastlogs/index.html  $WEBSITEBUCKET/reports/lastlogs/ --quiet
