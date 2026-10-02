# simple test script.
# need to delete the file first as the trigger is on s3CreateObject
aws s3 rm s3://ukmda-live/FF_UK009D_20260901_042214_746_0792832.jpg --profile ukmda_admin
aws s3 cp .\tests\FF_UK009D_20260901_042214_746_0792832.xml s3://ukmda-live/ --profile ukmda_admin
aws s3 cp .\tests\FF_UK009D_20260901_042214_746_0792832.jpg s3://ukmda-live/ --profile ukmda_admin
