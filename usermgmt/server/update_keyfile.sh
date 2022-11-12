#!/bin/bash

if [ "$(whoami)" != "root" ] ; then 
  echo "must be run as root"
  exit 0
fi

ls -1d /var/sftp/$1* | while read i 
do
  inif=$(ls -1 $i/live.key)
  source $inif
  echo "updating $inif"
  if [ "$S3FOLDER" == "" ] ; then 
    echo export S3FOLDER=\"archive/${CAMLOC}/\" >> $inif
  fi 
  if [ "$ARCHBUCKET" == "" ] ; then 
    echo export ARCHBUCKET=ukmon-shared >> $inif
  fi 
  if [ "$LIVEBUCKET" == "" ] ; then 
    echo export LIVEBUCKET=ukmon-live >> $inif
  fi 
  if [ "$WEBBUCKET" == "" ] ; then 
    echo export WEBBUCKET=ukmeteornetworkarchive >> $inif
  fi 
  if [ "$ARCHREGION" == "" ] ; then 
    echo export ARCHREGION=eu-west-2 >> $inif
  fi 
  if [ "$LIVEREGION" == "" ] ; then 
    echo export LIVEREGION=eu-west-1 >> $inif
  fi 
  if [ "$MATCHDIR" == "" ] ; then 
    echo export MATCHDIR=matches/RMSCorrelate >> $inif
  fi 
  statkeyf=$(echo $CAMLOC | tr '[:upper:]' '[:lower:]').key
  diff $inif /home/ec2-user/keymgmt/live/$statkeyf > /dev/null
  if [ $? -ne 0 ] ; then
    echo "updating master copy $statkeyf"
    \cp $inif /home/ec2-user/keymgmt/live/$statkeyf
  fi 
done

