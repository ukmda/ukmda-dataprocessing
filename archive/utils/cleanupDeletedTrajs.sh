#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# this script reads a list of logically-deleted trajectories from the sqlite database
# and moves the corresponding pickle and report data to a backup area
# These trajectories are generally duplicated events

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

cd ${DATADIR}/distrib

startdt=$(date --date="-$MATCHSTART days" '+%Y%m%d-080000')
jdt_min=$(python -c "from wmpl.Utils.TrajConversions import datetime2JD;import datetime;print(datetime2JD(datetime.datetime.strptime('$startdt', '%Y%m%d-%H%M%S')))")

echo "checking main storage, website and csvfiles"
sqlite3 $DATADIR/distrib/trajectories.db "select traj_file_path from trajectories where status=0 and jdt_ref > ${jdt_min} order by jdt_ref;" | while read traj ; do
   # check if there are two trajectories with the same folder - we don't want to delete the active one
   cnt=$(sqlite3 $DATADIR/distrib/trajectories.db "select count(traj_id)  from trajectories where traj_file_path='$traj';")
   moved=0
   if [ $cnt == 1 ] ; then 
      trajdir=$(dirname $traj)
      srcloc=${UKMONSHAREDBUCKET}/matches/RMSCorrelate/$trajdir
      trgloc=${UKMONSHAREDBUCKET}/matches/duplicates/$trajdir
      aws s3 ls $srcloc/ | awk -F " " '{print $4}' | while read fname; do
         aws s3 mv ${srcloc}/$fname ${trgloc}/$fname --quiet
         moved=1
      done 
      yr=${trajdir:13:4}
      trajpth=$(basename $trajdir)
      webloc=$WEBSITEBUCKET/reports/${yr}/orbits/$trajpth
      newloc=${UKMONSHAREDBUCKET}/matches/duplicates/reports/${yr}/orbits/$trajpth
      aws s3 ls $webloc/ | awk -F " " '{print $4}' | while read fname; do
         aws s3 mv $webloc/$fname $newloc/$fname --quiet
         moved=1
      done 

      trajpth1=${trajdir:34:19}
      csvname=$(echo $trajpth1 | sed 's/_/-/g')
      csvloc=${UKMONSHAREDBUCKET}/matches/${yr}/fullcsv
      newloc=${UKMONSHAREDBUCKET}/matches/duplicates/csvs/${yr}
      aws s3 ls $csvloc/ | awk -F " " '{print $4}' | grep $csvname | while read fname; do
         aws s3 mv $csvloc/$fname $newloc/$fname --quiet
         moved=1
      done 
      csvloc=$DATADIR/orbits/${yr}/fullcsv/processed
      ls -1 $csvloc/ | grep $csvname | while read fname; do
         aws s3 mv $csvloc/$fname $newloc/$fname --quiet
         moved=1
      done 
      [ $moved == 1 ] && echo "moved $trajpth"
   else
      echo skipping $traj
   fi 
done

echo "checking consolidated matches"
lasttraj=$(sqlite3 $DATADIR/distrib/trajectories.db "select traj_file_path from trajectories where status=0 and jdt_ref > ${jdt_min} order by jdt_ref;" | tail -1)
trajdir=$(dirname $lasttraj)
yr=${trajdir:13:4}
trajpth=$(basename $trajdir)
matchcsv=$DATADIR/matched/matches-full-${yr}.csv
grep $trajpth $matchcsv > /dev/null 
if [ $? == 0 ] ; then 
    python -c "from maintenance.dataMaintenance import removeDeletedTraj;removeDeletedTraj('$matchcsv')"
    python -m converters.toParquet $matchcsv
    aws s3 sync $DATADIR/matched/ $UKMONSHAREDBUCKET/matches/matched/ --include "*" --exclude "*.snap" --exclude "*.bkp" --exclude "*.gzip" --quiet
    aws s3 sync $DATADIR/matched/ $UKMONSHAREDBUCKET/matches/matchedpq/ --exclude "*" --include "*.snap" --exclude "*.bkp" --exclude "*.gzip" --quiet 
    aws s3 sync $DATADIR/matched/ $WEBSITEBUCKET/browse/parquet/  --exclude "*" --include "*.snap" --exclude "*.bkp" --exclude "*.gzip" --quiet

    srchcsv=$DATADIR/searchidx/${yr}-allevents.csv
    python -c "from maintenance.dataMaintenance import removeDeletedTraj;removeDeletedTraj('$srchcsv')"
    aws s3 sync  $DATADIR/searchidx/ $WEBSITEBUCKET/search/indexes/ --exclude "*" --include "*allevents.csv" --quiet 
fi 

echo "checking Mariadb Database"
python -c "from maintenance.dataMaintenance import removeDelTrajFromDb;removeDelTrajFromDb()"
