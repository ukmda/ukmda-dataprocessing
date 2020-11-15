#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/config.ini >/dev/null 2>&1

cp $here/main-index.shtml $REPORTDIR/index.shtml
cp $here/ukmon.css $REPORTDIR/

cd $REPORTDIR
echo "<table id=\"tablestyle\">" > yearlist.html
ls -1dr 2* | while read i
do
    echo "<tr><td><a href=\"$i/ALL\">$i Full Year</a></td><td></td></tr>" >> yearlist.html
    ls -1 $i | grep -v ALL | while read j
    do
        echo "<tr><td></td><td><a href=\"$i/$j\">$j</a></td></tr>" >> yearlist.html
    done
done
echo "</table>" >> yearlist.html
