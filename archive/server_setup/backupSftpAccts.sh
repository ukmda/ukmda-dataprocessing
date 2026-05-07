#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $here

bkpOneUser() {
    userid=$1
    srchost=$2
    mkdir -p ./backup/$userid
    sudo rsync -av $srchost:/var/sftp/$userid/ ./backup/$userid 
    sudo chown -R $USER:$USER ./backup/$userid
    cat ./backup/$userid/ukmon.ini | sed 's/3.11.55.160/batchserver.ukmeteors.co.uk/g' > /tmp/$userid.ini
    mv -f /tmp/$userid.ini ./backup/$userid/ukmon.ini
}

if [ $# -lt 2 ] ; then 
    echo "Usage: ./backupSftpAccounts.sh oldservername userfile"
    exit
fi 

echo "Warning: this must only be run on the new server"
read -p "press ctrl-c to quit or enter to continue"

oldserver=$1
srcfile=$2

cat $srcfile | while read stn
do 
    bkpOneUser $stn $oldserver
done