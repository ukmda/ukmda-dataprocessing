#!/bin/bash

#
# Create a report for the named shower and year
#
# Parameters
#   shower 3-letter code SSS
#   period to report on in yyyy or yyyymm format
#
# Consumes
#   All single-station and matched data from $DATADIR/single and $DATADIR/matched
#
# Produces
#   A report for the named shower, in $DATADIR/reports/yyyy/SSS
#   Which is then synced to the website

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

if [ $# -lt 2 ] ; then
	echo Usage: showerReport.sh GEM 2017 {force}
else
    shwr=$1
    dt=$2
    yr=${dt:0:4}
    mth=${dt:4:6}
    logger -s -t showerReport "starting $shwr $dt"
    source /home/ec2-user/venvs/${WMPL_ENV}/bin/activate
    export PYTHONPATH=$wmpl_loc:$PYLIB
    export MATCHDIR
    export DATADIR

    cd ${DATADIR}

    magval=999
    outdir=reports/$yr/$shwr
    if [ "$mth" != "" ] ; then
        outdir=$outdir/$mth
    fi 

    if [[ ! -d $DATADIR/reports/$yr/$shwr || "$3" == "force" ]] ; then
        logger -s -t showerReport "Running the analysis routines"
        python -m analysis.showerAnalysis.py $shwr $dt
        python -m reports.findFireballs $dt $shwr $magval

        if [ -f $MATCHDIR/RMSCorrelate/trajectories/${yr}/${dt}/plots/*${shwr}.png ] ; then 
            cp $MATCHDIR/RMSCorrelate/trajectories/${yr}/${dt}/plots/*${shwr}.png $DATADIR/$outdir
        fi 
        logger -s -t showerReport "done, now creating report"
    fi

    cd $DATADIR/$outdir

    sname=$(cat $DATADIR/$outdir/statistics.txt | head -1)
    idxfile=index.html
    cp $TEMPLATES/header.html $idxfile
    echo "<h2>$sname</h2>" >> $idxfile
    if [ "$mth" == "" ] ; then
        echo "<a href=\"/reports/index.html\">Back to report index</a><br>" >> $idxfile
        echo "</tr></table>" >> $idxfile
    else
        echo "<a href=\"/reports/$yr/$shwr/index.html\">Back to annual index</a><br>" >> $idxfile
    fi 
    echo "<pre>" >> $idxfile
    cat $DATADIR/$outdir/statistics.txt >> $idxfile
    if [ "$shwr" == "ALL" ] ; then 
        echo "Click <a href=\"/browse/annual/matches-${yr}.csv\">here</a> to download the matched data." >> $idxfile
    else
        echo "Click <a href=\"/browse/showers/$yr-$shwr-matches.csv\">here</a> to download the matched data." >> $idxfile
    fi
    echo "</pre>" >>$idxfile
    echo "<br>" >>$idxfile
    if [ -f fblist.txt ]  ; then 
        echo "\$(function() {" > reportindex.js
        echo "var table = document.createElement(\"table\");" >> reportindex.js
        echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> reportindex.js
        echo "var header = table.createTHead();" >> reportindex.js
        echo "header.className = \"h4\";" >> reportindex.js
        echo "var row = table.insertRow(-1);" >> reportindex.js
        echo "var cell = row.insertCell(0);" >> reportindex.js
        if [ "$magval" == "999" ] ; then 
            echo "cell.innerHTML = \"Brightest Ten Events\";" >> reportindex.js
        else 
            echo "cell.innerHTML = \"Fireball Reports\";" >> reportindex.js
        fi 

        cat $DATADIR/$outdir/fblist.txt | while read i ; do
            echo "var row = table.insertRow(-1);">> reportindex.js
            echo "var cell = row.insertCell(0);" >> reportindex.js
            fldr=$(echo $i | awk -F, '{print $1}')
            mag=$(echo $i | awk -F, '{print $2}')
            shwr=$(echo $i | awk -F, '{print $3}')
            bn=$(basename $(dirname $fldr))
            echo "cell.innerHTML = \"<a href="$fldr">$bn</a>\";" >> reportindex.js
            echo "var cell = row.insertCell(1);" >> reportindex.js
            echo "cell.innerHTML = \"$mag\";" >> reportindex.js
            echo "var cell = row.insertCell(2);" >> reportindex.js
            echo "cell.innerHTML = \"$shwr\";" >> reportindex.js
        done
        echo "var outer_div = document.getElementById(\"summary\");" >> reportindex.js
        echo "outer_div.appendChild(table);" >> reportindex.js
        echo "})" >> reportindex.js

        echo "<div class=\"row\">" >> $idxfile
        echo "<div class=\"col-lg-12\">" >> $idxfile
        echo "    <div id=\"summary\" class=\"table-responsive\"></div>" >> $idxfile
        echo "    <div id=\"reportindex\"></div>" >> $idxfile
        echo "</div>" >> $idxfile
        echo "</div>" >> $idxfile

        echo "<script src=\"./reportindex.js\"></script>" >> $idxfile
    fi
    if [[ "$mth" == "" && "$shwr" == "ALL" ]] ; then
        echo "<h3>Monthly Reports</h3>" >> $idxfile
        echo "<table class=\"table table-striped table-bordered table-hover table-condensed\"><tr>" >> $idxfile
        for i in 01 02 03 04 05 06  ; do
            if [ -d $DATADIR/$outdir/$i ] ; then 
                echo "<td><a href=\"./$i/index.html\">$i</a></td>" >> $idxfile
            fi        
        done 
        echo "</tr><tr>" >> $idxfile
        for i in 07 08 09 10 11 12 ; do
            if [ -d $DATADIR/$outdir/$i ] ; then 
                echo "<td><a href=\"./$i/index.html\">$i</a></td>" >> $idxfile
            fi        
        done
        echo "</tr></table>" >> $idxfile
    fi 
    echo "<h3>Additional Information</h3>" >> $idxfile
    echo "The graphs and histograms below show more information about the velocity, magnitude " >> $idxfile
    echo "start and end altitude and other parameters. Click for larger view. " >>$idxfile

    if [[ "$shwr" == "ALL" && "$mth" == "" ]] ; then
        cp $DATADIR/Annual-$2.jpg $DATADIR/$outdir/02_stream_plot_timeline_single.jpg
    fi

    if [ "$mth" == "" ]; then 
        dt=$(date +Y%m) 
    fi
    if [ -f $MATCHDIR/RMSCorrelate/trajectories/$yr/$dt/plots/*$shwr.png ] ; then 
        cp $MATCHDIR/RMSCorrelate/trajectories/$yr/$dt/plots/*$shwr.png .
    fi 
    jpglist=$(ls -1 *.jpg *.png)
    echo "<div class=\"top-img-container\">" >> $idxfile
    for j in $jpglist; do
        echo "<a href=\"./$j\"><img src=\"./$j\" width=\"20%\"></a>" >> $idxfile
    done
    echo "</div>" >> $idxfile

    echo "<script> \$('.top-img-container').magnificPopup({ " >> $idxfile
    echo "delegate: 'a', type: 'image', image:{verticalFit:false}, gallery:{enabled:true} }); " >> $idxfile
    echo "</script>" >> $idxfile

    cat $TEMPLATES/footer.html >> $idxfile


    logger -s -t showerReport "copying files to website"
    source $WEBSITEKEY
    aws s3 sync $DATADIR/$outdir $WEBSITEBUCKET/$outdir --quiet
    logger -s -t showerReport "all done"

    tstval=$(grep "$yr/$shwr" $DATADIR/reports/reportindex.js)
    if [ "$tstval" == "" ] ; then 
        ${SRC}/website/createReportIndex.sh ${yr}
    fi
    logger -s -t showerReport "finished"    
fi 
