# powershell script to add user to dailyReport email
# Copyright (C) 2018-2023 Mark McIntyre

set-location $psscriptroot
aws s3 cp s3://ukmon-shared/admin/dailyReportRecips.txt ./caminfo/ --profile ukmon-markmcintyre
cmd /c start /wait "C:\Program Files\TextPad 8\TextPad.exe" "caminfo\dailyReportRecips.txt"
Write-Output "uploading"
pause
aws s3 cp .\caminfo\dailyReportRecips.txt s3://ukmon-shared/admin/  --profile ukmon-markmcintyre
