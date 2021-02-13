#
# deployment script for website
#
if( $args[0] -eq "prod"){
    ~/scripts/set-aws-creds.ps1 ukmonarchive
    aws s3 sync .\static_content s3://ukmeteornetworkarchive/
} else {
    ~/scripts/set-aws-creds.ps1 mark-creds
    aws s3 sync .\static_content s3://mjmm-ukmonarchive.co.uk/
}
