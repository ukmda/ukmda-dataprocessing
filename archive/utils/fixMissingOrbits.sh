
ymd=20230814
yr=${ymd:0:4}
ym=${ymd:0:6}


targ=$WEBSITEBUCKET/reports/$yr/orbits/$ym/$ymd
orblist=$(aws s3 ls $targ/ | grep PRE | egrep -v "html|plots|png" | awk '{print $2}')

for orb in $orblist ; do
    srcdir=reports/$yr/orbits/${ym}/$ymd/${orb}
    aws s3 ls $OLDWEBSITEBUCKET/${srcdir}index.html > /dev/null
    if [ $? -eq 1 ] ; then
        aws s3 sync $WEBSITEBUCKET/$srcdir $OLDWEBSITEBUCKET/$srcdir
        pickname=${orb:0:15}_trajectory.pickle
        targdir=matches/RMSCorrelate/trajectories/$yr/$ym/$ymd/$orb
        aws s3 cp $WEBSITEBUCKET/reports/${yr}/orbits/${ym}/${ymd}/${orb}${pickname} $UKMONSHAREDBUCKET/$targdir
        aws s3 cp $WEBSITEBUCKET/reports/${yr}/orbits/${ym}/${ymd}/${orb}${pickname} $OLDUKMONSHAREDBUCKET/$targdir
    fi
done