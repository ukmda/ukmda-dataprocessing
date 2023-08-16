# Copyright (C) 2018-2023 Mark McIntyre 

# script to scan UKMON live data as it arrives for brightness information

import boto3


def lambda_handler(event, context):
    record = event['Records'][0]
    targbuck = 'ukmon-live'
    s3 = boto3.resource('s3')

    source = {'Bucket': 'ukmda-live', 'Key': record['s3']['object']['key']}
    s3.meta.client.copy(source, targbuck, record['s3']['object']['key'])
    #print(f"copied {record['s3']['object']['key']}")


# Test cases. Execute with "pytest ./curateLive.py"

def test_handler():
    event = {'Records': [{'s3':{'object':{'key':'test.txt'}}}]}
    lambda_handler(event, None)
