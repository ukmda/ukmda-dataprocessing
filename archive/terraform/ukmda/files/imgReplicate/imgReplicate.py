# Copyright (C) 2018-2023 Mark McIntyre 

# script to keep data synched between UKMDA and UKMON accounts

import boto3
import os


def lambda_handler(event, context):
    record = event['Records'][0]
    srcbuck= record['s3']['bucket']['name']
    fname = record['s3']['object']['key']
    if ('FF_' in fname and '.fits' in fname) or 'flux' in fname or 'flat' in fname:
        return 
    targwebbuck = os.getenv('TARGWEBBUCKET', default='ukmeteornetworkarchive')
    targshrbuck = os.getenv('TARGSHRBUCKET', default='ukmon-shared')
    if srcbuck == 'ukmda-shared':
        targbuck = targshrbuck
    else:
        targbuck = targwebbuck
    s3 = boto3.client('s3')
    src = {'Bucket': srcbuck, 'Key': fname}
    s3.copy_object(CopySource=src, Bucket=targbuck, Key=fname)
    print(f"copied {fname} to {targbuck}")
    return
