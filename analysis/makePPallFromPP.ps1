# simple script to create synthetic platepars_all_recalibrated file
$targpth=$args[0]

$ffname=(Get-ChildItem $targpth\FF*.fits).name
$hdr='{"'+$ffname+'": '
Write-Output $hdr > $targpth/platepars_all_recalibrated.json
(Get-Content -path $targpth/platepar_cmn2010.cal -Raw) -replace '"auto_recalibrated": false','"auto_recalibrated": true' >> $targpth/platepars_all_recalibrated.json
Write-Output "}" >> $targpth/platepars_all_recalibrated.json

