#!/bin/bash
# bash script to create monthly or annual index page for orbit data

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1

source $WEBSITEKEY

ym=$1
yr=${ym:0:4}
mth=${ym:4:2}

logger -s -t createOrbitIndex "creating orbit index page for $yr $mth"

if [ "$mth" != "" ] ; then
    displstr=${yr}-${mth}
    msg="Click on an entry to see results of analysis for the matched event."
    msg2="<a href=\"../index.html\">Back to annual index</a>" 
    targ=${WEBSITEBUCKET}/reports/${yr}/orbits/${ym}
    orblist=$(aws s3 ls $targ/ | grep PRE | grep $mth | awk '{print $2}')
    domth=1
    rm -f $DATADIR/orbits/$yr/$ym.txt
else
    displstr=${yr}
    msg="Click to explore each month."
    msg2="<a href=\"../../index.html\">Back to reports index</a>" 
    targ=${WEBSITEBUCKET}/reports/${yr}/orbits
    orblist=$(aws s3 ls $targ/ | grep PRE | grep $yr | awk '{print $2}')
    domth=0
fi

idxfile=/tmp/${ym}.html

cp $TEMPLATES/header.html $idxfile
echo "<div class=\"container\">" >> $idxfile
echo "<h2>Matched Event Orbit and Trajectory Reports for $displstr</h2>" >> $idxfile
echo "$msg2<hr>" >> $idxfile
echo "$msg<hr>" >> $idxfile
echo "<table class=\"table table-striped table-bordered table-hover table-condensed\"><tr>" >> $idxfile
j=0

if [ "$orblist" == "" ] ; then 
    echo "<td> No data available </td>" >> $idxfile
else
    for i in $orblist 
    do
        indir=$(basename $i)
        echo "<td><a href=$indir/index.html>$indir<a></td>" >> $idxfile
        ((j=j+1))
        if [ $j == 6 ] ; then
            j=0
            echo "</tr>" >> $idxfile
        fi
        if [ $domth -eq 1 ] ; then
            echo "$i" >> $DATADIR/orbits/$yr/$ym.txt
        fi
    done
fi
echo "</tr></table>" >> $idxfile
echo "</div>" >> $idxfile

if [ $domth -eq 0 ]
then
echo "<h3>Year to Date Density, Velocity and Solar Longitude</h3>" >> $idxfile
echo "Click on the charts to see a larger gallery view" >> $idxfile
echo "<div class=\"top-img-container\">" >> $idxfile
echo "<a href=\"/reports/plots/scecliptic_density.png\"><img src=\"/reports/plots/scecliptic_density.png\" width=\"30%\"></a>" >> $idxfile
echo "<a href=\"/reports/plots/scecliptic_sol.png\"><img src=\"/reports/plots/scecliptic_sol.png\" width=\"30%\"></a>" >> $idxfile
echo "<a href=\"/reports/plots/scecliptic_vg.png\"><img src=\"/reports/plots/scecliptic_vg.png\" width=\"30%\"></a>" >> $idxfile
echo "</div>" >> $idxfile
echo "<script> \$('.top-img-container').magnificPopup({ " >> $idxfile
echo "delegate: 'a', type: 'image', image:{verticalFit:false}, gallery:{enabled:true} }); " >> $idxfile
echo "</script>" >> $idxfile
fi

cat $TEMPLATES/footer.html >> $idxfile

logger -s -t createOrbitIndex "copying to website"

source $WEBSITEKEY
aws s3 cp $idxfile $targ/index.html --quiet
rm -f $idxfile

logger -s -t createOrbitIndex "finished"