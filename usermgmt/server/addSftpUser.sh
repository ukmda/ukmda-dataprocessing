#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# bash script to create new sftp user
#
userid=$1
shortid=$2
oldloc=$3
if [ -z $2 ] ; then shortid=$1 ; fi 

source ~/prod/config.ini
source ~/venvs/$WMPL_ENV/bin/activate

keydir=/home/ec2-user/keymgmt
cd $keydir

logger -s -t addSftpUser "adding user $userid at $shortid $oldloc"

# create the keyfiles in the required format
counter=0
ls $keydir/rawkeys/live/$shortid.key > /dev/null 2>&1
while [[ $? -ne 0  && $counter -ne 5 ]] ; do
    sleep 2
    logger -s -t addSftpUser "waiting for raw key for $shortid"   
    ls $keydir/rawkeys/live/$shortid.key > /dev/null 2>&1
    counter=$((counter + 1))
done 
if [ ! -f $keydir/rawkeys/live/$shortid.key ] ; then 
    logger -s -t addSftpUser "missing raw key for $shortid"   
    exit 1
fi 
python $keydir/jsonToKeyFile.py $keydir/rawkeys/live/$shortid.key $keydir/live

# all-lowercase versions of the names
userid="${userid,,}"
shortid_l="${shortid,,}"

if [ ! -f $keydir/live/$shortid_l.key ] ; then 
    logger -s -t addSftpUser "problem creating keyfile"
    exit 1
fi

# add a unix user and set their homedir to /var/sftp/userid
logger -s -t addSftpUser "Creating unix user $userid"
sudo useradd --system --shell /usr/sbin/nologin --groups sftp --home /var/sftp/$userid $userid
sudo mkdir /var/sftp/$userid
sudo chown root:sftp /var/sftp/$userid
sudo chmod 751 /var/sftp/$userid
sudo mkdir /var/sftp/$userid/.ssh

# copy the public key to the right place
logger -s -t addSftpUser "Applying the public key $1"
dos2unix $keydir/sshkeys/$1.pub
cat $keydir/sshkeys/$1.pub  > /tmp/tmp.pub
sudo cp /tmp/tmp.pub /var/sftp/$userid/.ssh/authorized_keys
sudo chown -R $userid:$userid /var/sftp/$userid/.ssh/authorized_keys
rm /tmp/tmp.pub

#create an empty client copy of the  ini file and make it writeable by the client
sudo touch /var/sftp/$userid/ukmon.ini.client 
sudo chown $userid:$userid /var/sftp/$userid/ukmon.ini.client 

# add the key to logupload's authorized_keys file
logger -s -t addSftpUser "Adding the key to loguploads authorized_keys"
awk 1 $keydir/sshkeys/*.pub > /tmp/logul.pub
sudo cp /tmp/logul.pub /var/sftp/logupload/.ssh/authorized_keys
sudo chown logupload:logupload /var/sftp/logupload/.ssh/authorized_keys
rm /tmp/logul.pub

# copy the files
logger -s -t addSftpUser "Copying the ini file and aws keyfile"
cat $keydir/ukmon.ini | sed "s/STATIONLOCATION/$userid/g" > /home/ec2-user/keymgmt/inifs/$userid.ini
sudo cp $keydir/inifs/$userid.ini /var/sftp/$userid/ukmon.ini
sudo cp $keydir/live/$shortid_l.key /var/sftp/$userid/live.key

# if we are moving a station, update the old ini file 
# so that the next run points to the new loc
if [ ! -z $oldloc ] ; then
    logger -s -t addSftpUser "Moving $oldloc to $userid"
    sudo cp /var/sftp/$oldloc/ukmon.ini /var/sftp/$oldloc/ukmon.ini.bkp
    sudo cp $keydir/inifs/$userid.ini /var/sftp/$oldloc/ukmon.ini
fi 
sudo ls -ltr /var/sftp/$userid/
sudo ls -ltr /var/sftp/$userid/.ssh/

logger -s -t addSftpUser "Finished"

# run these as root to create the structure
#  groupadd sftp
#  mkdir -p /var/sftp
#  chown root:root /var/sftp
#  chmod 751 /var/sftp

# Add this to /etc/ssh/sshd_config
# Match group sftp
#     ChrootDirectory /var/sftp/%u
#     AllowTCPForwarding no
#     X11Forwarding no
#     ForceCommand internal-sftp
#
# and then reload sshd 
#  service sshd reload
