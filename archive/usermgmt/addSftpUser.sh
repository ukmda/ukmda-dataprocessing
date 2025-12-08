#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# bash script to create new sftp user
#
userid=$1
shortid=$2
updatemode=$3
oldloc=$4

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $here

if [ -f ../config.ini ] ; then
    source ~/dev/config.ini
    keydir=/home/ec2-user/dev/keymgmt
else
    source ~/prod/config.ini
    keydir=/home/ec2-user/keymgmt

fi
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

cd $keydir

logger -s -t addSftpUser "adding user $userid $shortid $oldloc"

# wait for the file uploads to complete. For some reason paramiko does this asynchronously
counter=0
# all-lowercase versions of the names
userid="${userid,,}"
shortid_l="${shortid,,}"

ls $keydir/$shortid_l.key > /dev/null 2>&1
while [[ $? -ne 0  && $counter -ne 5 ]] ; do
    sleep 2
    logger -s -t addSftpUser "waiting for raw key for $shortid"   
    ls $keydir/keys/$shortid_l.key > /dev/null 2>&1
    counter=$((counter + 1))
done 
if [ ! -f $keydir/keys/$shortid_l.key ] ; then 
    logger -s -t addSftpUser "missing keyfile for $shortid"   
    exit 1
fi 

# add a unix user and set their homedir to /var/sftp/userid
grep -w $userid /etc/passwd
if [ $? -eq 1 ] ; then 
    dt=$(date +%Y-%m-%d)
    logger -s -t addSftpUser "Creating unix user $userid"
    sudo useradd --system --shell /usr/sbin/nologin --groups sftp --home /var/sftp/$userid --comment '${dt}' $userid
    sudo mkdir /var/sftp/$userid
    sudo chown root:sftp /var/sftp/$userid
    sudo chmod 751 /var/sftp/$userid
    # create the .ssh folder, platepar folder and empty client copy of the ini file
    sudo mkdir /var/sftp/$userid/.ssh
    sudo mkdir /var/sftp/$userid/platepar
    sudo touch /var/sftp/$userid/ukmon.ini.client
    # make these three writeable by the client
    sudo chown $userid:$userid /var/sftp/$userid/platepar /var/sftp/$userid/.ssh /var/sftp/$userid/ukmon.ini.client
else
    logger -s -t addSftpUser "Unix user $userid already exists"
fi
# copy the public key to the right place
logger -s -t addSftpUser "Applying the public key $userid"
dos2unix $keydir/sshkeys/$userid.pub
sudo cp $keydir/sshkeys/$userid.pub /var/sftp/$userid/.ssh/authorized_keys
sudo chown -R $userid:$userid /var/sftp/$userid/.ssh/authorized_keys
sudo chmod 644 /var/sftp/$userid/.ssh/authorized_keys

# add the key to logupload's authorized_keys file
logger -s -t addSftpUser "Adding the key to loguploads authorized_keys"
awk 1 $keydir/sshkeys/*.pub > /tmp/logul.pub
sudo cp /tmp/logul.pub /var/sftp/logupload/.ssh/authorized_keys
sudo chown logupload:logupload /var/sftp/logupload/.ssh/authorized_keys
rm /tmp/logul.pub

# copy the ini and aws key files
logger -s -t addSftpUser "Copying the ini file and aws keyfile"
sudo cp $keydir/inifs/$userid.ini /var/sftp/$userid/ukmon.ini
sudo cp $keydir/keys/$shortid_l.key /var/sftp/$userid/live.key
sudo cp $keydir/csvkeys/${shortid}.csv /var/sftp/$userid/$userid.csv
sudo dos2unix /var/sftp/$userid/live.key
sudo dos2unix /var/sftp/$userid/ukmon.ini
sudo dos2unix /var/sftp/$userid/$userid.csv
sudo chown $userid:$userid /var/sftp/$userid/$userid.csv /var/sftp/$userid/ukmon.ini /var/sftp/$userid/live.key

# if we are moving a station, update the old ini file 
# so that the next run points to the new loc
if [ ! -z $oldloc ] ; then
    logger -s -t addSftpUser "Moving $oldloc to $userid"
    sudo cp /var/sftp/$oldloc/ukmon.ini /var/sftp/$oldloc/ukmon.ini.bkp
    sudo cp $keydir/inifs/$userid.ini /var/sftp/$oldloc/ukmon.ini
    # and copy the ssh authorized keys file
    sudo cp $oldloc/.ssh/authorized_keys /var/sftp/$userid/.ssh/
    sudo chown -R $userid:$userid /var/sftp/$userid/.ssh/authorized_keys
    sudo chmod 644 /var/sftp/$userid/.ssh/authorized_keys
fi 

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
