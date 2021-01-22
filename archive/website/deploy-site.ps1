#
# deployment script for website
#

~/scripts/set-aws-creds.ps1 mark-creds

aws s3 sync .\static_content s3://mjmm-ukmonarchive.co.uk/

# site layout
# front page
#  summary by year of data captured
#   cameras, meteors, matches, fireballs
#
# Browse
#   by date
#       annual, monthly, weekly
#   by shower
#       each year
#
# Search
#   single date enter date/time and range (+/- minutes/hours)
#    get list of matches plus links to CSV orbit data
#       allow user to select other files to download 
#       create zip file 
# 