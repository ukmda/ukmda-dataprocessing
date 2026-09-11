#!/bin/bash
#

# DEPLOY THIS TO THE OLD SERVER in ~/server_setup

sudo su << EOD
cd /var/sftp
grep -R HELPER /var/sftp/*/ukmon.ini
EOD
