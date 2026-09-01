# simple test script.
# need to delete the file first as the trigger is on s3CreateObject
aws s3 rm s3://ukmda-live/M20260901_042214_axminster_n_UK009DP.jpg --profile ukmda_admin
aws s3 cp .\tests\M20260901_042214_axminster_n_UK009D.xml s3://ukmda-live/ --profile ukmda_admin
aws s3 cp .\tests\M20260901_042214_axminster_n_UK009DP.jpg s3://ukmda-live/ --profile ukmda_admin
