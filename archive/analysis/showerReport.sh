#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

if [ $# -lt 2 ] ; then
	echo Usage: showerReport.sh GEM 2017 {force}
else
    logger -s -t showerReport "starting $1 $2"
    source /home/ec2-user/venvs/${WMPL_ENV}/bin/activate
    export PYTHONPATH=$wmpl_loc:$PYLIB

    cd ${DATADIR}

    if [[ ! -d reports/$2/$1 || "$3" == "force" ]] ; then
        logger -s -t showerReport "Running the analysis routines"
        export DATADIR
        python $PYLIB/analysis/showerAnalysis.py $1 $2
        python $PYLIB/reports/findFireballs.py $2 $DATADIR/reports/$2/$1 $1
        logger -s -t showerReport "done, now creating report"
    fi
    cd ${DATADIR}/reports/$2/$1
    sname=$(cat statistics.txt | head -1)
    idxfile=index.html
    cp $TEMPLATES/header.html $idxfile
    echo "<h2>$sname</h2>" >> $idxfile
    echo "<a href=\"/reports/index.html\">Back to report index</a><hr>" >> $idxfile
    echo "<pre>" >> $idxfile
    cat statistics.txt >> $idxfile
    echo "Click <a href=\"/browse/showers/$2-$1-matches.csv\">here</a> to download the processed data." >> $idxfile
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
        echo "cell.innerHTML = \"Fireball Reports\";" >> reportindex.js

        cat ./fblist.txt | while read i ; do
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
    echo "<h3>Additional Information</h3>" >> $idxfile
    echo "The graphs and histograms below show more information about the velocity, magnitude " >> $idxfile
    echo "start and end altitude and other parameters. Click for larger view. " >>$idxfile

    if [ "$1" == "ALL" ] ; then
        cp $DATADIR/Annual-$2.jpg ./02_stream_plot_timeline_single.jpg
    fi
    jpglist=$(ls -1 *.jpg)
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
    aws s3 sync . $WEBSITEBUCKET/reports/$2/$1 --quiet
    logger -s -t showerReport "all done"

    tstval=$(grep "$2/$1" $DATADIR/reports/reportindex.js)
    if [ "$tstval" == "" ] ; then 
        ${SRC}/website/createReportIndex.sh
    fi
    logger -s -t showerReport "finished"    
fi 
