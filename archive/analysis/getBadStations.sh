#!/bin/bash
#
# bash to get list of stations excluded from analysis
#

source ~/.ssh/ukmon-markmcintyre-keys
uxt=$(date -d 'yesterday' +%s000)
js=$(aws logs filter-log-events --log-group-name "/aws/lambda/consolidateFTPdetect" --start-time $uxt --filter-pattern "too many")
echo $js | jq '.events | .[] | .message'
