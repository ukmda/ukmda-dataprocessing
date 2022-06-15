#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

/usr/bin/aws ec2 start-instances --instance-ids $BKPINSTANCEID
