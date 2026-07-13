# Copyright (C) 2018-2023 Mark McIntyre
$here=$PSScriptRoot
# sam build --profile ukmonshared --region eu-west-1
sam local invoke --profile ukmonshared -e $here/test1.json  --region eu-west-1 > $here/new_output.txt
Write-Output "any differences will appear between the lines"
write-output "======"
Compare-Object (Get-Content $here/expected_output_1.txt)  (Get-Content $here/new_output.txt)
write-output "======"

sam local invoke --profile ukmonshared -e $here/test2.json  --region eu-west-1 > $here/new_output.txt
write-output "any differences will appear between the lines"
write-output "======"
Compare-Object (Get-Content $here/expected_output_2.txt)  (Get-Content $here/new_output.txt)
write-output "======"
