aws cloudwatch get-metric-statistics --metric-name Duration --start-time 2020-02-08T00:00:00 --end-time 2020-02-12T23:59:59 --namespace AWS/Lambda --dimensions Name=FunctionName,Value=ConsolidateCSVs --period 300 --statistics Sum > ConsolidateCSVs1.json
aws cloudwatch get-metric-statistics --metric-name Duration --start-time 2020-02-13T00:00:00 --end-time 2020-02-17T23:59:59 --namespace AWS/Lambda --dimensions Name=FunctionName,Value=ConsolidateCSVs --period 300 --statistics Sum > ConsolidateCSVs2.json
aws cloudwatch get-metric-statistics --metric-name Duration --start-time 2020-02-08T00:00:00 --end-time 2020-02-12T23:59:59 --namespace AWS/Lambda --dimensions Name=FunctionName,Value=CSVTrigger --period 300 --statistics Sum > CSVTrigger1.json
aws cloudwatch get-metric-statistics --metric-name Duration --start-time 2020-02-13T00:00:00 --end-time 2020-02-17T23:59:59 --namespace AWS/Lambda --dimensions Name=FunctionName,Value=CSVTrigger --period 300 --statistics Sum > CSVTrigger2.json

(get-content -path .\ConsolidateCSVs1.json | convertfrom-json).Datapoints | convertto-csv -notypeinformation | set-content ConsolidateCSVs1.csv
(get-content -path .\ConsolidateCSVs2.json | convertfrom-json).Datapoints | convertto-csv -notypeinformation | set-content ConsolidateCSVs2.csv
(get-content -path .\CSVTrigger1.json | convertfrom-json).Datapoints | convertto-csv -notypeinformation | set-content CSVTrigger1.csv
(get-content -path .\CSVTrigger2.json | convertfrom-json).Datapoints | convertto-csv -notypeinformation | set-content CSVTrigger2.csv

del Consoli*.json
del CSVTrigger*.json
