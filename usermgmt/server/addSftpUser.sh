#!/bin/bash
#
# bash script to create new sftp user
#
userid=$1
shortid=$2
oldloc=$3
if [ -z $2 ] ; then shortid=$1 ; fi 

cd /home/ec2-user/keymgmt

# create the keyfiles in the required format
python /home/ec2-user/keymgmt/jsonToKeyFile.py rawkeys/live/$shortid.key live

# all-lowercase versions of the names
userid="${userid,,}"
shortid_l="${shortid,,}"

if [ ! -f live/$shortid_l.key ] ; then 
    echo "problem creating keyfile"
    sleep 30
    exit 1
fi

# add a unix user and set their homedir to /var/sftp/userid
sudo useradd --system --shell /usr/sbin/nologin --groups sftp --home /var/sftp/$userid $userid
sudo mkdir /var/sftp/$userid
sudo chown root:sftp /var/sftp/$userid
sudo chmod 751 /var/sftp/$userid
sudo mkdir /var/sftp/$userid/.ssh

# copy the public key to the right place
dos2unix /home/ec2-user/keymgmt/sshkeys/$1.pub
cat /home/ec2-user/keymgmt/sshkeys/$1.pub  > /tmp/tmp.pub
sudo cp /tmp/tmp.pub /var/sftp/$userid/.ssh/authorized_keys
sudo chown -R $userid:$userid /var/sftp/$userid/.ssh/authorized_keys

# add the key to logupload's authorized_keys file
awk 1 ~ec2-user/keymgmt/sshkeys/*.pub > /tmp/logul.pub
sudo cp /tmp/logul.pub /var/sftp/logupload/.ssh/authorized_keys
sudo chown logupload:logupload /var/sftp/logupload/.ssh/authorized_keys
rm /tmp/logul.pub

# copy the files
cat /home/ec2-user/keymgmt/ukmon.ini | sed "s/STATIONLOCATION/$userid/g" > /home/ec2-user/keymgmt/inifs/$userid.ini
sudo cp /home/ec2-user/keymgmt/inifs/$userid.ini /var/sftp/$userid/ukmon.ini
#sudo cp /home/ec2-user/keymgmt/arch/$shortid_l.key /var/sftp/$userid/archive.key
sudo cp /home/ec2-user/keymgmt/live/$shortid_l.key /var/sftp/$userid/live.key

# if we are moving a station, update the old ini file 
# so that the next run points to the new loc
if [ ! -z $oldloc ] ; then
    sudo cp /var/sftp/$oldloc/ukmon.ini /var/sftp/$oldloc/ukmon.ini.bkp
    sudo cp /home/ec2-user/keymgmt/inifs/$userid.ini /var/sftp/$oldloc/ukmon.ini
fi 
sudo ls -ltr /var/sftp/$userid/
sudo ls -ltr /var/sftp/$userid/.ssh/


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
