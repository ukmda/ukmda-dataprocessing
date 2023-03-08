#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
# Fireballs page
#
# Obtain a list of fireballs and create the page with links
#
# Parameters
#   yyyy year to process
# 
# Consumes
#   matched/matches-full-yyyy.csv, looking for confirmed fireballs
#
# Produces
#   a webpage and javascript table with links to the events
#    synced to the website
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
logger -s -t createFireballPage "starting"
$SRC/utils/clearCaches.sh

if [ $# -eq 0 ]; then
    yr=$(date +%Y)
else
    yr=$1
fi

logger -s -t createFireballPage "creating fireball page for $yr"

mkdir -p $DATADIR/reports/$yr/fireballs > /dev/null 2>&1
cd $DATADIR/reports/$yr/fireballs

source $HOME/venvs/$WMPL_ENV/bin/activate
python -m reports.findFireballs ${yr} ALL $2

echo "\$(function() {" > reportindex.js
echo "var table = document.createElement(\"table\");" >> reportindex.js
echo "table.className = \"table table-striped table-bordered table-hover table-condensed w-100\";" >> reportindex.js
echo "table.setAttribute(\"id\", \"fbtableid\");" >>reportindex.js

if [ -f ./fblist.txt ] ; then 
    cat ./fblist.txt | while read i ; do
        echo "var row = table.insertRow(-1);">> reportindex.js
        echo "var cell = row.insertCell(0);" >> reportindex.js
        fldr=$(echo $i | awk -F, '{print $1}')
        mag=$(echo $i | awk -F, '{print $2}')
        shwr=$(echo $i | awk -F, '{print $3}')
        md=$(echo $i | awk -F, '{print $4}')
        md=${md:0:15}
        img=$(grep besti ./${md}.md | awk '{print $2}')

        if [ "${fldr:0:1}" == "_" ] ; then 
            echo "cell.innerHTML = \"${fldr:1:25}\";" >> reportindex.js
        else 
            bn=$(basename $(dirname $fldr))
            echo "cell.innerHTML = \"<a href="$fldr">$bn</a>\";" >> reportindex.js
        fi
        echo "var cell = row.insertCell(1);" >> reportindex.js
        echo "cell.innerHTML = \"$mag\";" >> reportindex.js
        echo "var cell = row.insertCell(2);" >> reportindex.js
        echo "cell.innerHTML = \"$shwr\";" >> reportindex.js
        if [ "$img" != "" ]; then 
            echo "var cell = row.insertCell(3);" >> reportindex.js
            echo "cell.innerHTML = \"<a href="$fldr"><img src=$img width=100px></a>\";" >> reportindex.js
        fi 
    done
else
        echo "var row = table.insertRow(-1);">> reportindex.js
        echo "var cell = row.insertCell(0);" >> reportindex.js
        echo "cell.innerHTML = \"Data unavailable\";" >> reportindex.js
fi 
echo "var header = table.createTHead();" >> reportindex.js
echo "var row = header.insertRow(0);" >> reportindex.js
echo "var cell = row.insertCell(0);" >> reportindex.js
echo "cell.innerHTML = \"Fireball Reports\";" >> reportindex.js
echo "var cell = row.insertCell(1);" >> reportindex.js
echo "cell.innerHTML = \"Vis Mag\";" >> reportindex.js
echo "var cell = row.insertCell(2);" >> reportindex.js
echo "cell.innerHTML = \"Shower\";" >> reportindex.js
echo "var cell = row.insertCell(3);" >> reportindex.js
echo "cell.innerHTML = \"Image Link\";" >> reportindex.js

echo "var outer_div = document.getElementById(\"summary\");" >> reportindex.js
echo "outer_div.appendChild(table);" >> reportindex.js
echo "})" >> reportindex.js
echo "\$(document).ready(function() {" >> reportindex.js
# need single quotes here to allow the hash to be printed
echo '$("#fbtableid").DataTable({' >> reportindex.js
echo "columnDefs : [" >> reportindex.js
echo "{ Type : \"numeric\", targets : [2]}" >> reportindex.js
echo "	]," >> reportindex.js
echo "order : [[ 1, \"asc\"],[2,\"desc\"]]," >> reportindex.js
echo "paging: false" >> reportindex.js
echo "});});" >> reportindex.js

cp $TEMPLATES/fbreportindex.html index.html

logger -s -t createFireballPage "copy to website"

aws s3 sync $DATADIR/reports/$yr/fireballs/  $WEBSITEBUCKET/reports/$yr/fireballs/ --quiet

$SRC/utils/clearCaches.sh
logger -s -t createFireballPage "finished"
