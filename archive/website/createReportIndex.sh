#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

if [[ "$here" == *"prod"* ]] ; then
    echo sourcing prod config
    source $HOME/prod/config/config.ini >/dev/null 2>&1
else
    echo sourcing dev config
    source $HOME/src/config/config.ini >/dev/null 2>&1
fi

cd ${SRC}/analysis/REPORTS
echo "\$(function() {" > $here/data/reportindex.js
echo "var table = document.createElement(\"table\");" >> $here/data/reportindex.js
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $here/data/reportindex.js
echo "var header = table.createTHead();" >> $here/data/reportindex.js
echo "header.className = \"h4\";" >> $here/data/reportindex.js
ls -1dr 2* | while read i
do
    echo "var row = table.insertRow(-1);" >> $here/data/reportindex.js
    echo "var cell = row.insertCell(0);" >> $here/data/reportindex.js
    echo "cell.innerHTML = \"<a href="$i/ALL/index.html">$i Full Year</a>\";" >> $here/data/reportindex.js
    echo "var cell = row.insertCell(1);" >> $here/data/reportindex.js
    echo "cell.innerHTML = \"<a href="$i/orbits/index.html">Orbits</a>\";" >> $here/data/reportindex.js

    ls -1 $i | egrep -v "ALL|orbits" | while read j
    do
        echo "var row = table.insertRow(-1);">> $here/data/reportindex.js
        echo "var cell = row.insertCell(0);" >> $here/data/reportindex.js
        echo "var cell = row.insertCell(1);" >> $here/data/reportindex.js
        sname=`grep $j $CONFIG/streamnames.csv | awk -F, '{print $2}'`
        echo "cell.innerHTML = \"<a href="$i/$j/index.html">$sname</a>\";" >> $here/data/reportindex.js
    done
done
echo "var outer_div = document.getElementById(\"summary\");" >> $here/data/reportindex.js
echo "outer_div.appendChild(table);" >> $here/data/reportindex.js
echo "})" >> $here/data/reportindex.js

source $WEBSITEKEY
aws s3 cp $here/data/reportindex.js  $WEBSITEBUCKET/data/
