# Copyright (C) 2018-2023 Mark McIntyre
Content-Type: multipart/mixed; boundary="//"
MIME-Version: 1.0

--//
Content-Type: text/cloud-config; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="cloud-config.txt"

#cloud-config
cloud_final_modules:
- [scripts-user, always]

--//
Content-Type: text/x-shellscript; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="userdata.txt"

#!/bin/bash
for fldr in admin consolidated fireballs kmls videos matches archive
do 
    /usr/bin/logger -s -t backupUkmon starting $fldr
    /bin/time -f "runtime %E" /usr/bin/aws s3 sync s3://ukmon-shared/$fldr s3://ukmon-shared-backup/$fldr 
done 
/bin/time -f "runtime %E" /usr/bin/aws s3 sync s3://ukmeteornetworkarchive s3://ukmon-shared-backup/websitebackup
sudo shutdown  -h now
--//--