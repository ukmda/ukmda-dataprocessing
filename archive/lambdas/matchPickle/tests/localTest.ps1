# Copyright (C) 2018-2023 Mark McIntyre
$here=$PSScriptRoot
$x = (sam local invoke --profile ukmonshared -e $here/testEvent.json  --region eu-west-1 | convertfrom-json)
$x.body | set-content .\tests\new_output.txt
Write-Output "any differences will appear between the lines"
write-output "======"
Compare-Object (Get-Content $here/testResult.json)  (Get-Content $here/new_output.txt)
write-output "======"

