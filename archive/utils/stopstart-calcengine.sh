#!/bin/bash

# script to create RMS shower association details if not already present
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

source /home/ec2-user/venvs/${RMS_ENV}/bin/activate
source $SERVERAWSKEYS
AWS_DEFAULT_REGION=eu-west-2
aws ec2 $1-instances --instance-ids $SERVERINSTANCEID
if [ "$1" == "start "] ; then 
    privip=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].PrivateIpAddress --output text)
    export BIGSERVER=$privip
else
    export BIGSERVER=
fi 