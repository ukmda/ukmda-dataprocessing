#!/bin/bash

# bash script to create index page for an individual orbit report

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/orbitsolver.ini > /dev/null 2>&1

ym=$1
yr=${ym:0:4}
mth=${ym:4:2}

idxfile=${results}/${yr}/orbits/${yr}${mth}/$1/index.shtml
repf=`ls -1 ${results}/${yr}/orbits/${yr}$mth/${ym}/$yr*report.txt`
repfile=`basename $repf`
pref=${repfile:0:16}

echo "<html><head><title>Orbit Report for $ym</title></head>" > $idxfile
echo "<body><h1>Orbital Analysis for matched events on $ym</h1>" >> $idxfile

echo "<a href=\"${pref}orbit_top.png\"><img src=\"${pref}orbit_top.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}orbit_side.png\"><img src=\"${pref}orbit_side.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}ground_track.png\"><img src=\"${pref}ground_track.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}velocities.png\"><img src=\"${pref}velocities.png\" width=\"20%\"></a>" >> $idxfile

echo "<p>More graphs below the text report<br></p>" >>$idxfile
echo "<pre><!--#include file=\"$repfile\" --></pre>" >>$idxfile

echo "<a href=\"${pref}lengths.png\"><img src=\"${pref}lengths.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}lags_all.png\"><img src=\"${pref}lags_all.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}all_spatial_residuals.png\"><img src=\"${pref}all_spatial_residuals.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}total_spatial_residuals_length_grav.png\"><img src=\"${pref}total_spatial_residuals_length_grav.png\" width=\"20%\"></a>" >> $idxfile
echo "<br>">>$idxfile
echo "<a href=\"${pref}abs_mag.png\"><img src=\"${pref}abs_mag.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}abs_mag_ht.png\"><img src=\"${pref}abs_mag_ht.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}all_angular_residuals.png\"><img src=\"${pref}all_angular_residuals.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}all_spatial_total_residuals_height.png\"><img src=\"${pref}all_spatial_total_residuals_height.png\" width=\"20%\"></a>" >> $idxfile
echo "<br>">>$idxfile
echo "<a href=\"${pref}all_spatial_residuals_length.png\"><img src=\"${pref}all_spatial_residuals_length.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}total_spatial_residuals_length.png\"><img src=\"${pref}total_spatial_residuals_length.png\" width=\"20%\"></a>" >> $idxfile

echo "</body></html>" >> $idxfile

