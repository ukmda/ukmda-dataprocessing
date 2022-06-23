#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1

# backup job is automatically run as a startup script on this server
# via the userdata field
/usr/bin/aws ec2 start-instances --instance-ids $BKPINSTANCEID
