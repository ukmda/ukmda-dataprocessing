# powershell script to get API details for use in other code
# Copyright (C) 2018-2023 Mark McIntyre

$outf=$psscriptroot + "/apis-mm.txt"
$apis=(aws apigateway get-rest-apis --profile default --region eu-west-1 | convertfrom-json)

clear-content -path $outf
foreach ($itm in $apis.items) {
    $id = $itm.id
    $nam = $itm.name  
    $outstr = $nam + " " + $id
    write-output $outstr >> $outf
}