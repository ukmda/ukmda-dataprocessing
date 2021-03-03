#
# deployment script for website
#
$devurl='https://0zbnc358p0.execute-api.eu-west-1.amazonaws.com/test'
$prdurl='https://lx6dt0krxj.execute-api.eu-west-1.amazonaws.com/prod'

$bsjs=".\templates\searchdialog-template.js"
$newf=".\static_content\data\searchdialog.js"

if( $args[0] -eq "prod"){
    ((Get-Content -path $bsjs -Raw) -replace '{{APIURL}}',$prdurl) | Set-Content -Path $newf
    ~/scripts/set-aws-creds.ps1 ukmonarchive
    aws s3 sync .\static_content s3://ukmeteornetworkarchive/
} else {
    ((Get-Content -path $bsjs -Raw) -replace '{{APIURL}}',$devurl) | Set-Content -Path $newf
    ~/scripts/set-aws-creds.ps1 mark-creds
    aws s3 sync .\static_content s3://mjmm-ukmonarchive.co.uk/
}
