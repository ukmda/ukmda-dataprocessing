#!/bin/bash
lastlog=$(ls -1tr $SRC/logs/nightly-*.log | tail -1)
lastmtch=$(ls -1tr $SRC/logs/matches-*.log | tail -1)

egrep "nightlyJob|consolidateOutput|createMthlyExtracts|createShwrExtracts|createSearchable|createFireballPage|showerReport|reportYear|createSummaryTable|createLatestTable|stationReports" $lastlog > /tmp/logmsgs.txt
egrep "findAllMatches1|convertUfoToRms|getRMSSingleData|runMatching" $lastmtch > /tmp/matchpt1.txt
egrep "findAllMatches2|updateIdexPages|createOrbitIndex" $lastmtch > /tmp/matchpt2.txt

cp $TEMPLATES/header.html $DATADIR/lastlog.html
echo "<pre>" >> $DATADIR/lastlog.html
head -2 /tmp/logmsgs.txt >> $DATADIR/lastlog.html
cat /tmp/matchpt1 >> $DATADIR/lastlog.html
python -m reports.getSolutionStati $lastmtch >> $DATADIR/lastlog.html
cat /tmp/matchpt2 >> $DATADIR/lastlog.html
len=$(wc -l /tmp/logmsgs.txt|awk '{print $1}')
len=$((len-2))
tail -$len /tmp/logmsgs.txt >> $DATADIR/lastlog.html
echo "</pre>" >> $DATADIR/lastlog.html
cat $TEMPLATES/footer.html >> $DATADIR/lastlog.html
rm /tmp/matchpt1.txt /tmp/matchpt2 /tmp/logmsgs.txt