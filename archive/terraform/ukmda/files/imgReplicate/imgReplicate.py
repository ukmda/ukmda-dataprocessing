# Copyright (C) 2018-2023 Mark McIntyre 

# script to scan UKMON live data as it arrives for brightness information

import boto3
import os


def lambda_handler(event, context):
    record = event['Records'][0]
    srcbuck= record['s3']['bucket']['name']
    fname = record['s3']['object']['key']
    targbuck = os.getenv('TARGBUCKET', default='ukmeteornetworkarchive')
    s3 = boto3.client('s3')
    src = {'Bucket': srcbuck, 'Key': fname}
    s3.copy_object(CopySource=src, Bucket=targbuck, Key=fname)
    print(f"copied {fname}")
