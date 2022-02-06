#!/bin/bash
# bash script to create index page for an individual orbit report
#
# Parameters
#   full path to the folder to create an index for
#   (optional) "force" to compel the script to recreate the index
#
# Consumes
#   The ftpdetect and platepar files, to create the csv and extracsv files
#
# Produces
#   Website index.html for the event, along with any images, videos and graphs
#     all synced to the website


if [ $# -lt 1 ] ; then
    echo "usage: createPageIndex.sh /full/path/to/folder {force}"
    echo "optionally force recalc of extra data files"
    exit 1
fi 

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1
source $HOME/venvs/$WMPL_ENV/bin/activate

logger -s -t createPageIndex "starting"

if [ "$2" == "force" ] ; then
    cd $SRC/orbits
    echo "forcing recalc of extra files"
    logger -s -t createPageIndex "generate extra data files and copy other data of interest"
    python -m traj.extraDataFiles $1
fi
cd $here

logger -s -t createPageIndex "generating orbit page index.html"
ym=$(basename $1)
yr=${ym:0:4}
mth=${ym:0:6}
ymd=${ym:0:8}
targ=${WEBSITEBUCKET}/reports/${yr}/orbits/${mth}/${ymd}/$ym

#Examples of arg1
#/home/ec2-user/ukmon-shared/matches/RMSCorrelate/trajectories/20211009_043016.566_UK
#/home/ec2-user/ukmon-shared/matches/RMSCorrelate/trajectories/2021/202101/20210131/20210131_052556.356_UK
srcdata=$1

idxfile=${srcdata}/index.html
repf=$(ls -1 ${srcdata}/$yr*report.txt)
repfile=$(basename $repf)
pref=${repfile:0:16}

fldr=$(basename $srcdata)

cp $TEMPLATES/header.html $idxfile
echo "<h2>Orbital Analysis for matched events on $ym</h2>" >> $idxfile
echo "<a href=\"../index.html\">Back to daily index</a><hr>" >> $idxfile
echo "<pre>" >> $idxfile
cat ${srcdata}/summary.html >> $idxfile
echo "Click <a href=\"./$fldr.zip\">here</a> to download a zip of the raw and processed data." >> $idxfile
echo "</pre>" >>$idxfile
echo "<p><b>Detailed report below graphs</b></p>" >>$idxfile
echo "<h3>Click on an image to see a larger view</h3>" >> $idxfile

echo "<div class=\"top-img-container\">" >> $idxfile
echo "<a href=\"${pref}orbit_top.png\"><img src=\"${pref}orbit_top.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}orbit_side.png\"><img src=\"${pref}orbit_side.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}ground_track.png\"><img src=\"${pref}ground_track.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}velocities.png\"><img src=\"${pref}velocities.png\" width=\"20%\"></a>" >> $idxfile
echo "<br>">>$idxfile

cat ${srcdata}/jpgs.html >> $idxfile

echo "<a href=\"${pref}lengths.png\"><img src=\"${pref}lengths.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}lags_all.png\"><img src=\"${pref}lags_all.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}abs_mag.png\"><img src=\"${pref}abs_mag.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}abs_mag_ht.png\"><img src=\"${pref}abs_mag_ht.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}all_angular_residuals.png\"><img src=\"${pref}all_angular_residuals.png\" width=\"20%\"></a>" >> $idxfile
echo "<a href=\"${pref}all_spatial_total_residuals_height.png\"><img src=\"${pref}all_spatial_total_residuals_height.png\" width=\"20%\"></a>" >> $idxfile
echo "</div>" >> $idxfile

echo "<div>" >> $idxfile
cat ${srcdata}/mpgs.html >> $idxfile
echo "</div>" >> $idxfile

echo "<pre>" >>$idxfile 
cat $repf >>$idxfile
echo "</pre>" >>$idxfile
echo "<br>">>$idxfile

echo "<script> \$('.top-img-container').magnificPopup({ " >> $idxfile
echo "delegate: 'a', type: 'image', image:{verticalFit:false}, gallery:{enabled:true} }); " >> $idxfile
echo "</script>" >> $idxfile

cat $TEMPLATES/footer.html >> $idxfile

logger -s -t createPageIndex "adding zip file"
zip -j -r -9 /tmp/$fldr.zip ${srcdata} -x ${srcdata}/$fldr.zip -x ${srcdata}/?pgs.lst -x ${srcdata}/?pgs.html --quiet
mv -f /tmp/$fldr.zip ${srcdata}/

logger -s -t createPageIndex "copying to website"
source $WEBSITEKEY
aws s3 sync ${srcdata}/ ${targ}/ --include "*" --quiet

logger -s -t createPageIndex "finished"
