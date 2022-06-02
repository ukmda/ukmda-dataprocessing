#
# source the EE AWS keys
. ~/.ssh/ukmon-markmcintyre.ps1

$loggroups=@('consolidateKmls', 'consolidateJpgs', 'ConsolidateCSVs', 'consolidateLatest', 
    'consolidateFTPdetect','matchDataApiHandler','CSVTrigger','searchUKmon')

foreach ($log in $loggroups) {
    Write-Output $log
    aws logs put-retention-policy --log-group-name "/aws/lambda/${log}" --retention-in-days 30 --region eu-west-2
}

$loggroups=@('fetchECSV-fetchECSV-lGYUkVXiWCR4', 'dailyReport', 
'createUkmonLiveIndexes',  'MonitorLiveFeed')

foreach ($log in $loggroups) {
    Write-Output $log
    aws logs put-retention-policy --log-group-name "/aws/lambda/${log}" --retention-in-days 30 --region eu-west-1
}