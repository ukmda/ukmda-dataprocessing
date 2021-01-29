#!/bin/bash

# bash script to create index page for an individual orbit report

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini > /dev/null 2>&1

ym=$1
yr=${ym:0:4}
mth=${ym:4:2}

datadir=${REPORTDIR}/${yr}/orbits/${yr}${mth}/$1
targ=${WEBSITEBUCKET}/reports/${yr}/orbits/${yr}${mth}/$1/

idxfile=${datadir}/index.html
repf=`ls -1 ${datadir}/$yr*report.txt`
repfile=`basename $repf`
pref=${repfile:0:16}

cp $TEMPLATES/header.html $idxfile
echo "<div class=\"container\">" >> $idxfile
echo "<h2>Orbital Analysis for matched events on $ym</h2>" >> $idxfile
echo "<pre>" >>$idxfile
cat ${datadir}/summary.html >>$idxfile
echo "</pre>" >>$idxfile
echo "<h3>Click on an image to see a larger view</h3>" >> $idxfile

echo "<a href=\"${pref}orbit_top.png\"><img src=\"${pref}orbit_top.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}orbit_side.png\"><img src=\"${pref}orbit_side.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}ground_track.png\"><img src=\"${pref}ground_track.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}velocities.png\"><img src=\"${pref}velocities.png\" width=\"20%\"></a>" >> $idxfile
echo "<br>">>$idxfile

ls -1 ${datadir}/*.jpg | while read jpg 
do
    jpgbn=`basename $jpg`
    echo "<a href=\"$jpgbn\"><img src=\"$jpgbn\" width=\"20%\"></a>" >> $idxfile
done
echo "<br>">>$idxfile

echo "<p>More graphs below the detailed report<br></p>" >>$idxfile
echo "<pre>" >>$idxfile 
cat $repf >>$idxfile
echo "</pre>" >>$idxfile
echo "<a href=\"${pref}lengths.png\"><img src=\"${pref}lengths.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}lags_all.png\"><img src=\"${pref}lags_all.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}abs_mag.png\"><img src=\"${pref}abs_mag.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}abs_mag_ht.png\"><img src=\"${pref}abs_mag_ht.png\" width=\"20%\"></a>" >> $idxfile
echo "<br>">>$idxfile
echo "<a href=\"${pref}all_spatial_residuals.png\"><img src=\"${pref}all_spatial_residuals.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}total_spatial_residuals_length_grav.png\"><img src=\"${pref}total_spatial_residuals_length_grav.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}all_angular_residuals.png\"><img src=\"${pref}all_angular_residuals.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}all_spatial_total_residuals_height.png\"><img src=\"${pref}all_spatial_total_residuals_height.png\" width=\"20%\"></a>" >> $idxfile

cat $TEMPLATES/footer.html >> $idxfile

source $WEBSITEKEY
aws s3 sync ${datadir}/ $targ --include "*" 

