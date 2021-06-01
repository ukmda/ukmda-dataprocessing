#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source ~/.ssh/ukmon-backup-keys
aws s3 sync s3://ukmon-shared/ s3://ukmon-shared-backup/ --source-region eu-west-1 --region eu-west-2

find /home/ec2-user/prod/logs -name "backupUkmonShared*.log" -mtime +30 -exec rm -f {} \;
