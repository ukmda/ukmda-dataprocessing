#
# deployment script for website
#

~/scripts/set-aws-creds.ps1 mark-creds

get-content template-header.html, template-mainpage.html, template-footer.html | set-content index.html
get-content template-header.html, template-about.html, template-footer.html | set-content about.html

aws s3 sync . s3://mjmm-ukmonarchive.co.uk --exclude "template*"  --exclude "deploy*"

Remove-Item .\index.html
Remove-Item .\about.html
