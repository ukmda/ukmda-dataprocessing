#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# script to generate a user audit report and email it to me
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

echo "{\"Subject\": {\"Data\": \"User Audit\",\"Charset\": \"utf-8\"}," > $DATADIR/admin/auditmsg.json
echo -n "\"Body\": {\"Text\": {\"Data\": \"" >> $DATADIR/admin/auditmsg.json

# general audit of all users
export AWS_PROFILE=ukmonshared
python -m maintenance.getUserAndKeyInfo audit > $DATADIR/admin/useraudit.txt

# accounts not used for 30 days or more
export MAXAGE=30
python -m maintenance.getUserAndKeyInfo dormant >> $DATADIR/admin/useraudit.txt

awk -v ORS='\\n' '1' $DATADIR/admin/useraudit.txt >> $DATADIR/admin/auditmsg.json
echo "\",\"Charset\": \"utf-8\"}}}" >> $DATADIR/admin/auditmsg.json

pushd $DATADIR/admin
aws ses send-email --destination ToAddresses="markmcintyre99@googlemail.com" --message file://auditmsg.json --from "noreply@ukmeteors.co.uk" --region eu-west-2
popd
rm $DATADIR/admin/auditmsg.json

unset MAXAGE
unset AWS_PROFILE
