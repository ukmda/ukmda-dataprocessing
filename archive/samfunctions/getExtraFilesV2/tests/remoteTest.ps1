# Copyright (C) 2018-2023 Mark McIntyre
# test 
if ($args.count -eq 0) {
    aws lambda invoke --profile ukmonshared --function-name getExtraOrbitFilesV2 --log-type Tail --cli-binary-format raw-in-base64-out --payload file://tests/testEvent.json  --region eu-west-2 ./ftpdetect.log
    aws lambda invoke --profile ukmonshared --function-name getExtraOrbitFilesV2 --log-type Tail --cli-binary-format raw-in-base64-out --payload file://tests/testEvent2.json  --region eu-west-2 ./ftpdetect.log
}
else {
    $orbit = $args[0]
    $yr = $orbit.substring(0,4)
    $ym = $orbit.substring(0,6)
    $ymd = $orbit.substring(0,8)
    $pickfile = $orbit.substring(0,15) + '_trajectory.pickle'
    $pickle = "$yr/$ym/$ymd/$orbit/$pickfile"
    ((Get-Content -path tests\templateEvent.json -Raw) -replace "PUTKEYHERE","$pickle") | Set-Content -Path tests\dummy.json
    aws lambda invoke --profile ukmonshared --function-name getExtraOrbitFilesV2 --log-type Tail --cli-binary-format raw-in-base64-out --payload file://tests/dummy.json  --region eu-west-2 ./ftpdetect.log
    Remove-Item tests\dummy.json
}
    
