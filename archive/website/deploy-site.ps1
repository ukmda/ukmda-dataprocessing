#
# deployment script for website
#

~/scripts/set-aws-creds.ps1 mark-creds

get-content header.template, mainpage.template, footer.template | set-content index.html
get-content header.template, about.template, footer.template | set-content about.html

aws s3 sync . s3://mjmm-ukmonarchive.co.uk --exclude "*.template"  --exclude "deploy*"

Remove-Item .\index.html
Remove-Item .\about.html
