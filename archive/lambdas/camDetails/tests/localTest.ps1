# Copyright (C) 2018- Mark McIntyre
$here=$PSScriptRoot
# sam build --profile ukmonshared --region eu-west-1
sam local invoke --profile ukmonshared -e $here/test.json  --region eu-west-1 > $here/new_output.txt
Write-Outpute-Output "any differences will appear between the lines"
Write-Output "======"
Compare-Object (Get-Content $here/expected_output.txt)  (Get-Content $here/new_output.txt)
Write-Output "======"
