# Copyright (C) 2018-2023 Mark McIntyre 

# script to scan UKMON live data as it arrives for brightness information

import boto3
import os


def lambda_handler(event, context):
    record = event['Records'][0]
    targbuck = 'ukmon-live'
    s3 = boto3.resource('s3')
    jpgname = record['s3']['object']['key']
    xmlname = jpgname[:-5]+'.xml'

# this is a bit shit. I should be able to just copy the objects, but for some reason this doesn't trigger
# the website page update process
    s3.meta.client.download_file('ukmda-live', jpgname, '/tmp/' + jpgname)
    s3.meta.client.download_file('ukmda-live', xmlname, '/tmp/' + xmlname)
    s3.meta.client.upload_file('/tmp/' + jpgname, targbuck, jpgname, ExtraArgs={'ContentType': 'image/jpeg'})
    s3.meta.client.upload_file('/tmp/' + xmlname, targbuck, xmlname, ExtraArgs={'ContentType': 'application/xml'})
    os.remove('/tmp/' + jpgname)
    os.remove('/tmp/' + xmlname)

#    jpgsource = {'Bucket': 'ukmda-live', 'Key': jpgname}
#    xmlsource = {'Bucket': 'ukmda-live', 'Key': xmlname}
#    s3.meta.client.copy_object(CopySource=jpgsource, Bucket=targbuck, Key=jpgname) #, ACL='bucket-owner-full-control')
#    s3.meta.client.copy_object(CopySource=xmlsource, Bucket=targbuck, Key=xmlname) #, ACL='bucket-owner-full-control')
    print(f"copied {jpgname}")


# Test cases. Execute with "pytest ./curateLive.py"

def test_handler():
    event = {'Records': [{'s3':{'object':{'key':'test.txt'}}}]}
    lambda_handler(event, None)
