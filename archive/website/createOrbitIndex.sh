#!/bin/bash
# bash script to create daily, monthly or annual index page for orbit data
#
# Parameters
#   yyyymmdd to run for (or yyyymm or yyyy)
#
# Consumes
#   If doing daily index, scans website for solutions to include in the index. 
#   If doing monthly or annual index, scans site for days or months to include. 
#
# Produces
#   Website index pages for the day, month or year, synced to the website

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1

source $WEBSITEKEY

ym=$1
yr=${ym:0:4}
mth=${ym:4:2}
dy=${ym:6:2}

logger -s -t createOrbitIndex "creating orbit index page for $yr $mth $dy"

if [ "$dy" != "" ] ; then
    displstr=${yr}-${mth}-${dy}
    msg="Click on an entry to see results of analysis for the matched event."
    msg2="<a href=\"../index.html\">Back to monthly index</a>" 
    targ=${WEBSITEBUCKET}/reports/${yr}/orbits/${yr}${mth}/${ym}
    orblist=$(ls -1 ${MATCHDIR}/RMSCorrelate/trajectories/${yr}/${yr}${mth}/${ym} | egrep -v "plots|png" )
    domth=1
    doplt=0
    rm -f $DATADIR/orbits/$yr/$ym.txt
elif [ "$mth" != "" ] ; then
    displstr=${yr}-${mth}
    msg="Click to explore the selected day."
    msg2="<a href=\"../index.html\">Back to annual index</a>" 
    targ=${WEBSITEBUCKET}/reports/${yr}/orbits/${ym}
    orblist=$(ls -1 ${MATCHDIR}/RMSCorrelate/trajectories/${yr}/${ym} | egrep -v "plots|png")
    domth=1
    doplt=1
    rm -f $DATADIR/orbits/$yr/$ym.txt
else
    displstr=${yr}
    msg="Click to explore the selected month."
    msg2="<a href=\"../../index.html\">Back to reports index</a>" 
    targ=${WEBSITEBUCKET}/reports/${yr}/orbits
    orblist=$(ls -1 ${MATCHDIR}/RMSCorrelate/trajectories/${yr} | egrep -v "plots|png")
    domth=0
    doplt=1
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

if [ $doplt -eq 1 ]
then
echo "<h3>Density, Velocity and Solar Longitude for the current period</h3>" >> $idxfile
echo "Click on the charts to see a larger gallery view" >> $idxfile
echo "<div class=\"top-img-container\">" >> $idxfile
echo "<a href=\"./plots/scecliptic_density.png\"><img src=\"./plots/scecliptic_density.png\" width=\"30%\"></a>" >> $idxfile
echo "<a href=\"./plots/scecliptic_sol.png\"><img src=\"./plots/scecliptic_sol.png\" width=\"30%\"></a>" >> $idxfile
echo "<a href=\"./plots/scecliptic_vg.png\"><img src=\"./plots/scecliptic_vg.png\" width=\"30%\"></a>" >> $idxfile
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