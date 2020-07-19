# scan the live stream for potential matches

import os, sys, datetime
import boto3
import botocore
from urllib.parse import unquote_plus

def lambda_handler(event, context):
    # check which account we're in
    client = boto3.client('sts')
    response = client.get_caller_identity()['Account']
    if response == '317976261112':
        target = 'mjmm-live'
    else:
        target = 'ukmon-live'
    # work out the prefix we want to check 
    dd=datetime.date.today()-datetime.timedelta(days=1)
    pref='M{:04d}{:02d}{:02d}'.format(dd.year, dd.month, dd.day)
    # connect to S3 bucket and get list of files
    conn = boto3.client('s3') 
    for key in conn.list_objects(Bucket=target, Prefix=pref, Suffix='xml')['Contents']:
        print(key['Key'])
    

