# Copyright (C) 2018-2023 Mark McIntyre
import json
import os
import boto3
import pandas as pd 


def getS3Client():
    sts_client = boto3.client('sts')
    try: 
        assumed_role_object=sts_client.assume_role(
            RoleArn="arn:aws:iam::822069317839:role/service-role/S3FullAccess",
            RoleSessionName="AssumeRoleSession1")
        credentials=assumed_role_object['Credentials']
        s3 = boto3.resource('s3',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])    
    except:
        with open('awskeys','r') as inf:
            lis = inf.readlines()
        s3 = boto3.resource('s3',
            aws_access_key_id=lis[0].strip(),
            aws_secret_access_key=lis[1].strip(),
            region_name = 'eu-west-2')
    return s3


def lambda_handler(event, context):
    s3 = getS3Client()

    print('received event', json.dumps(event))
    qs = event['queryStringParameters']
    reqval = qs['camid']

    tmpdir = os.getenv('TMP', default='/tmp')
    srcbucket = os.getenv('ARCHBUCKET', default='ukmda-shared')
    srckey = 'consolidated/camera-details.csv'
    targfile = os.path.join(tmpdir, 'camera-details.csv')
    s3.meta.client.download_file(srcbucket, srckey, targfile)
    df = pd.read_csv(targfile)
    if reqval != 'ALL':
        df = df[df.camid == reqval]

        pstr = {'camid':df.iloc[-1].camid, 'loc': df.iloc[-1].site, 'dir': df.iloc[-1].sid}
    else:
        pstr = {'all'}
    return {
        'statusCode': 200,
        'body': pstr #json.loads(pstr) 
    }
           

if __name__ == '__main__':
    evt = {'queryStringParameters': {'camid':'UK0006'}}
    pstr = lambda_handler(evt, True)
    js = json.loads(pstr)
    print(js)
