#!/bin/bash


addOneUser() {
    userid=$1
    $srchost=$2
    grep -w $userid /etc/passwd
    if [ $? -eq 1 ] ; then 
        dt=$(date +%Y-%m-%d)
        logger -s -t addSftpUser "Creating unix user $userid"
        sudo useradd --system --shell /usr/sbin/nologin --groups sftp --home /var/sftp/$userid --comment "${dt}" $userid
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
    echo sudo rsync -av $srchost:/var/sftp/$userid/ /var/sftp/$userid 
}

oldserver=$1
srcfile=$2

cat $srcfile | while read stn
do 
    addOneUser $stn $oldserver
done