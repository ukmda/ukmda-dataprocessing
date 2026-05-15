#!/bin/bash
#

sudo su << EOD
cd /var/sftp
grep -R HELPER /var/sftp/*/ukmon.ini| grep -v batch  
EOD
