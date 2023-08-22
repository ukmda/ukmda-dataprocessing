#
# Function to save an FTPdetect file and platepar as ECSV files
# Copyright (C) 2018-2023 Mark McIntyre
#
import boto3
import os

def lambda_handler(event, context):
    record = event['Records'][0]
    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']
    targbuck = os.getenv('TARGBUCKET', default='NONE')
    if targbuck != 'NONE':
        s3 = boto3.client('s3')
        print(f'copying {s3object} to {targbuck}')
        res = s3.list_objects_v2(Bucket=s3bucket,Prefix=s3object)
        if res['KeyCount'] > 0:
            for ent in res['Contents']:
                key = ent['Key']
                if 'flux' in key or 'FF_' in key or '.bmp' in key:
                    continue
                s3.copy_object(Bucket=targbuck, Key=key, CopySource={'Bucket': s3bucket, 'Key': key})    
    return 0
