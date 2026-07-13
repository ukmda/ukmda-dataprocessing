# Copyright (C) 2018-2023 Mark McIntyre
$here=$PSScriptRoot
# sam build --profile ukmonshared --region eu-west-1
sam local invoke --profile ukmonshared -e $here/test.json > $here/new_output.txt

Write-Output "the URLs will be different each time this is run, but you should be able to ctrl-click on a link"

Get-Content $here/new_output.txt
